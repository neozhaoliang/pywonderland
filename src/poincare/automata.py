# -*- coding: utf-8 -*-

import pygraphviz as pgv
import re

# this small alphabet suffice for our purpose
# modify it manually if necessary
SIGMA = [0, 1, 2]


class Automaton:
    """
    To build an automaton, just name an automaton state as the starting state, then all states that are 
    reachable from this start will automatically be assigned a number.
    
    The advantage of this approach of representating an automaton is that all the "dead states"
    (states that are not reachable from the start) are automatically discarded.
    
    The disadvantage is that you can not see all the states and the transition table at the first glance.
    So let's write a draw() function to visualize it!
    """
    
    def __init__(self, initial):
        self.initial = initial
        self.num_states = self.number_states(self.initial, 0)
    
    def number_states(self, state, next_number):
        if state.number is None:
            state.number = next_number
            next_number += 1
            for symbol, target in state.all_transitions():
                next_number = self.number_states(target, next_number)
        return next_number 

    def draw(self, filename, program="dot"):
        """
        use graphviz to draw the automaton
        this depends on the "pygraphviz" module
        """
        G = pgv.AGraph(strict=False, directed=True, rankdir="LR")
        self.initial.draw(G, set(), color="red")
        G.draw(filename, prog=program)
        return self
        

class AutomatonState:
    
    def __init__(self, accept=False):
        self.accept = accept
        self.number = None  
        self.transitions = dict()
        
    def all_transitions(self):
        raise NotImplementedError
        
    def add_transition(self):
        raise NotImplementedError

    def draw(self, G, seen, color="black"):
        if self in seen:
            return

        seen.add(self)
        
        if self.accept:
            G.add_node(self.number, shape="doublecircle", color=color)
        else:
            G.add_node(self.number, shape="circle", color=color)

        for symbol, target in self.all_transitions():
            target.draw(G, seen)
            if symbol is None:
                label = u"\u03b5"
            else:
                label = symbol
            G.add_edge(self.number, target.number, label=label)


class NFA(Automaton):
    
    def __init__(self, initial):
        Automaton.__init__(self, initial)
        
    def asDFA(self):
        return NFA_to_DFA(self)()
   

class DFA(Automaton):
    
    def __init__(self, initial):
        Automaton.__init__(self, initial)
    
    def minimize(self):
        return Hopcroft(self)()
   

class NFAState(AutomatonState):
    
    def __init__(self, accept=False):
        AutomatonState.__init__(self, accept)

    def add_transition(self, symbol, target):
        try:
            self.transitions[symbol].add(target)
        except:
            self.transitions[symbol] = {target}
    
    def all_transitions(self):
        transitions = set()
        for symbol, targets in self.transitions.items():
            transitions |= { (symbol, target) for target in targets }
        return transitions
            
    def epsilon_closure(self):
        
        epsilon_closure = {self}
        stack = [self]
        
        while stack:
            state = stack.pop()
            for target in state.transitions.get(None, set()):
                if target not in epsilon_closure:
                    stack.append(target)
                    epsilon_closure.add(target)
                    
        return frozenset(epsilon_closure)


class DFAState(AutomatonState):
    
    def __init__(self, accept=False):
        AutomatonState.__init__(self, accept)
        
    def add_transition(self, symbol, target):
        if symbol is None:
            raise ValueError("DFA can not contain epsilon transitions")
        if symbol in self.transitions:
            raise ValueError("state already contains given transition")
        
        self.transitions[symbol] = target
        
    def all_transitions(self):
        return set(self.transitions.items())
    

class NFA_to_DFA:
    
    def __init__(self, nfa):
        self.initial = nfa.initial
        
    def __call__(self):
        
        q0 = self.initial.epsilon_closure()
        Q = {q0: self.construct_dfa_state_from_subset(q0)}
        
        stack = [q0]
        while stack:
            q = stack.pop()
            
            for symbol in SIGMA:
                t = self.delta_closure(q, symbol)
                
                if t:
                    try:
                        dfa_state = Q[t]
                    except:
                        dfa_state = self.construct_dfa_state_from_subset(t)
                        Q[t] = dfa_state
                        stack.append(t)
                        
                    Q[q].add_transition(symbol, dfa_state)
                    
        return DFA(Q[q0])

    def delta_closure(self, q, c):
        """
        compute the epsilon closure of the set q under transition c
        """
        delta_closure = set()
        for state in q:
            for target in state.transitions.get(c, set()):
                delta_closure |= target.epsilon_closure()

        return frozenset(delta_closure)
        
        
    def construct_dfa_state_from_subset(self, q):
        """
        return a new DFA state corresponding the subset q
        if q contains any final state then the returned DFA state is also final
        otherwise it's non-final
        """
        for state in q:
            if state.accept == True:
                return DFAState(True)
        return DFAState(False)
        
        
class Hopcroft:
    
    def __init__(self, dfa):
        self.initial = dfa.initial  
        self.P = self.initial_partition()
        
    def __call__(self):
        try:
            s1, s2 = self.initial_partition()
            if len(s1) <= len(s2):
                W = {s1}
            else:
                W = {s2}
        except:
            W = self.initial_partition()
            
        while W:
            A = W.pop()
            for c in SIGMA:
                
                # We should be careful that if we modify a set while iterating over it then unpredictable things would happen.
                # So iterate over another but same partition!
                T = frozenset(self.P)
                for Y in T:
                    S = self.split(Y,c,A)
                    if S:
                        s1, s2 = S
                        self.P.remove(Y)
                        self.P.add(s1)
                        self.P.add(s2)

                        if Y in W:
                            W.remove(Y)
                            W.add(s1)
                            W.add(s2)
                        else:
                            if len(s1) <= len(s2):
                                W.add(s1)
                            else:
                                W.add(s2)
                                
        # now self.P is our final partition
        # let's make it a DFA
        result_dfa = dict()
        
        def aux(subset):
            state = next(iter(subset))
            dfa_state = DFAState(state.accept)
            result_dfa[subset] = dfa_state

            for symbol, target in state.transitions.items():
                target_subset = self.current_partition_containing(target)

                if target_subset not in result_dfa:
                    aux(target_subset)
                dfa_state.add_transition(symbol, result_dfa[target_subset])
                
            return dfa_state
            
        initial_subset = self.current_partition_containing(self.initial)
        return DFA(aux(initial_subset))
        
    def initial_partition(self):
        """
        partition all the states into accepted and non-accepted
        """
        s1 = set()
        s2 = set()

        def aux(state):
            if state.accept == True:
                s1.add(state)
            else:
                s2.add(state)
            for target in state.transitions.values():
                if target not in set.union(s1, s2):
                    aux(target)
                    
        aux(self.initial)
        
        """
        be careful of the case that all states are accepted
        """
        if s1 and s2:
            return {frozenset(s1), frozenset(s2)}
        return {frozenset(s1)}
            
    def split(self, S, c, B):
        """
        try to split set S into two subsets {s1, s2} by a pair (B, c)
        if not splitted then return None
        """
        s1 = set()
        s2 = set()
        
        for x in S:
            y = x.transitions.get(c, None)
            if y in B:
                s1.add(x)
            else:
                s2.add(x)
        if s1 and s2:
            return {frozenset(s1), frozenset(s2)}
        return None
        
    def current_partition_containing(self, state):
        """
        return the subset that contains the given state in current partition
        """
        for p in self.P:
            if state in p:
                return p
        raise ValueError("partition does contain given state, something must be wrong")
        return None


def Parse(filename):
    f = open(filename, "r")
    T = dict()
    initial = None

    while True:
        L = f.readline()
        if L:
            
            # if L is a comment line or a blank line
            if len(L) < 2 or L[0] == "#":
                continue
            
            s = re.search("([0-9]+):", L)
            if s:
                num = int(s.group(1))
                try:
                    state = T[num]
                except:
                    state = NFAState()
                    T[num] = state

                s = re.findall("([0-9]+)+[ ]+([0-9]+)", L)
                for w in s:
                    a = int(w[0])
                    b = int(w[1])
                    try:
                        target = T[b]
                    except:
                        target = NFAState()
                        T[b] = target

                    state.add_transition(a, target)

                s = re.findall("None[ ]+([0-9]+)", L)
                for w in s:
                    b = int(w)
                    try:
                        target = T[b]
                    except:
                        target = NFAState()
                        T[b] = target

                    state.add_transition(None, target)

                s = re.search("A", L)
                if s:
                    state.accept = True

                s = re.search("S", L)
                if s:
                    initial = state

                continue

        else:
            break
        
    f.close()
    return NFA(initial)

#----------------------------------------------------
# Example Usage:
# fsm = Parse("worstcase.txt").draw("asNFA.png").asDFA().draw("asDFA.png").minimize().draw("minimized.png")
# OK I know the worst case is exponentially larger and cannot be minimized ...
#------------------------------------------------------
