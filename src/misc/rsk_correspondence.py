"""
ManimGL Demonstration of the Robinson-Schensted-Knuth (RSK) Correspondence.

This script visualizes the RSK algorithm, demonstrating how a permutation π
uniquely corresponds to a pair of Standard Young Tableaux (P, Q) of the
same shape.

Usage:
    manimgl rsk_correspondence.py RSK          # Run the insertion process
    manimgl rsk_correspondence.py RSKInverse   # Run the inverse/recovery process
"""

from copy import deepcopy
from manimlib import *

# =============================================================================
# 1. Algorithm Layer
# =============================================================================


def schensted_insert(P, x):
    """
    Standard RSK insertion algorithm.
    Returns:
        - P_new: The updated tableau structure.
        - chain: A list of animation steps containing (value, old_pos, new_pos).
    """
    P_new = deepcopy(P)
    chain = []
    row_idx = 0
    curr_val = x
    old_rc = None

    while True:
        # Case 1: The tableau is empty or we reached the bottom.
        # Create a new row with the current value.
        if row_idx == len(P_new):
            P_new.append([curr_val])
            chain.append((curr_val, old_rc, (row_idx, 0)))
            break

        row = P_new[row_idx]
        # Find the first element in the current row that is larger than curr_val.
        col_idx = next((i for i, v in enumerate(row) if v > curr_val), None)

        # Case 2: No element is larger. Append curr_val to the end of this row.
        if col_idx is None:
            row.append(curr_val)
            chain.append((curr_val, old_rc, (row_idx, len(row) - 1)))
            break
        # Case 3: Found a larger element. Bump it (kick it out).
        else:
            kicked_val = row[col_idx]
            chain.append((curr_val, old_rc, (row_idx, col_idx)))

            # Replace the value in the row
            row[col_idx] = curr_val

            # The kicked value becomes the new current value to be inserted in the next row
            curr_val = kicked_val
            old_rc = (row_idx, col_idx)
            row_idx += 1

    return P_new, chain


def reverse_schensted(P, start_r, start_c):
    """
    Inverse RSK algorithm to recover the value from position (start_r, start_c).
    Returns:
        - chain: Animation steps for the bumping path.
        - curr_val: The final value ejected from the tableau.
    """
    # Remove the starting value from P
    val = P[start_r].pop(start_c)
    if not P[start_r]:
        P.pop(start_r)

    chain = []
    curr_r = start_r
    curr_val = val

    # Move upwards through the tableau
    while curr_r > 0:
        prev_r = curr_r - 1
        row = P[prev_r]

        # Find the rightmost element in the previous row that is smaller than curr_val
        target_c = -1
        target_val = -1
        for c, v in enumerate(row):
            if v < curr_val:
                target_c = c
                target_val = v
            else:
                break

        # Record the step: moving value, target position, and the value being kicked
        chain.append(
            {"moving": curr_val, "target": (prev_r, target_c), "kicked": target_val}
        )

        # Perform the swap in data
        P[prev_r][target_c] = curr_val
        curr_val = target_val
        curr_r -= 1

    return chain, curr_val


# =============================================================================
# 2. Base Scene (Visual Utilities)
# =============================================================================


class RSKBase(Scene):
    BOX_SIZE = 0.8

    def setup_headers(self, sub_text):
        """Creates the main title and the specific subtitle."""
        title = (
            Text("The Robinson–Schensted–Knuth correspondence").scale(0.7).to_edge(UP)
        )
        sub = (
            Text(sub_text).scale(0.5).set_color(GREY_A).next_to(title, DOWN, buff=0.15)
        )
        self.play(FadeIn(title), FadeIn(sub))
        return sub

    def setup_tableaux_layout(self, ref_obj):
        """
        Calculates the positions for Tableau P and Q based on a reference object
        (either the Pi input string or the Result slots).
        """
        label_y = ref_obj.get_bottom()[1] - 0.6

        p_lbl = Text("Insertion tableau P").scale(0.6).move_to([-3.5, label_y, 0])
        q_lbl = Text("Recording tableau Q").scale(0.6).move_to([3.5, label_y, 0])
        self.play(FadeIn(p_lbl), FadeIn(q_lbl))

        # Calculate origin points for the grids
        self.P_origin = np.array([-5.1, label_y - 1.2, 0])
        self.Q_origin = np.array([1.9, label_y - 1.2, 0])

        # Initialize dictionaries to track Mobjects
        # keys: 'P' or 'Q' -> (row, col) -> Square Mobject
        self.boxes = {"P": {}, "Q": {}}
        # keys: 'P' or 'Q' -> value (int) -> Text Mobject
        self.mobs = {"P": {}, "Q": {}}

    def get_pos(self, r, c, origin):
        """Calculates absolute position for a grid cell."""
        return origin + np.array([c * self.BOX_SIZE, -r * self.BOX_SIZE, 0])

    def create_visual_cell(self, r, c, val, origin, key):
        """
        Creates a box and a number text at a specific grid coordinate.
        Registers them in the internal dictionaries.
        """
        pos = self.get_pos(r, c, origin)

        # Create the square box
        box = Rectangle(width=self.BOX_SIZE, height=self.BOX_SIZE).set_stroke(WHITE, 2)
        box.move_to(pos)

        # Create the number text
        text = Text(str(val)).scale(0.7).move_to(pos)

        # Register in dictionaries
        self.boxes[key][(r, c)] = box
        self.mobs[key][val] = text

        return box, text

    def generate_tableau_group(self, data, origin, key):
        """Generates a VGroup containing the full tableau (for static drawing)."""
        group = VGroup()
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                box, text = self.create_visual_cell(r, c, val, origin, key)
                group.add(box, text)
        return group


# =============================================================================
# 3. Forward Scene (Insertion)
# =============================================================================


class RSK(RSKBase):
    def construct(self):
        # 1. Setup Titles
        sub_lbl = self.setup_headers("Construct (P, Q) from π")

        # 2. Setup Input Display (Pi)
        perm = [3, 1, 4, 10, 5, 9, 2, 8, 6, 7]
        pi_mobs = VGroup(*[Text(str(x)).scale(0.8) for x in perm])
        pi_group = VGroup(Text("π = (").scale(0.8), *pi_mobs, Text(")").scale(0.8))
        pi_group.arrange(RIGHT, buff=0.4).next_to(sub_lbl, DOWN, buff=0.7)

        self.play(Write(pi_group))

        # 3. Initialize Layout based on Pi position
        self.setup_tableaux_layout(pi_group)

        P_data = []
        Q_data = []
        bump_vec = 0.6 * self.BOX_SIZE * DOWN

        # 4. Main Animation Loop
        for k, x in enumerate(perm):
            # Highlight current input number
            self.play(pi_mobs[k].animate.set_color(YELLOW), run_time=0.2)

            # Execute Insertion Algorithm
            P_data, chain = schensted_insert(P_data, x)

            # Animate the Insertion Chain
            for i, (val, old_rc, new_rc) in enumerate(chain):
                # Determine which object is moving
                if old_rc is None:
                    # It's a new number coming from Pi
                    mob_moving = (
                        Text(str(val)).scale(0.7).set_color(YELLOW).move_to(pi_mobs[k])
                    )
                    self.add(mob_moving)
                    self.mobs["P"][val] = mob_moving
                else:
                    # It's an existing number inside the tableau
                    mob_moving = self.mobs["P"][val]

                target = self.get_pos(*new_rc, self.P_origin)
                is_bump = i < len(chain) - 1

                anims = [mob_moving.animate.move_to(target).set_color(WHITE)]

                # If landing in a new spot, create a new box
                if new_rc not in self.boxes["P"]:
                    box, _ = self.create_visual_cell(*new_rc, 0, self.P_origin, "P")
                    # Remove the dummy text created by create_visual_cell
                    # because we want to use the flying 'mob_moving' instead
                    del self.mobs["P"][0]
                    anims.append(ShowCreation(box))

                if not is_bump:
                    # Case: Settle into position
                    self.play(*anims, run_time=0.7, rate_func=smooth)
                else:
                    # Case: Bump collision
                    next_val = chain[i + 1][0]
                    mob_kicked = self.mobs["P"][next_val]

                    # Move incoming to target, move resident out (bump)
                    anims.append(
                        mob_kicked.animate.move_to(target + bump_vec).set_color(RED)
                    )
                    self.play(
                        AnimationGroup(*anims, lag_ratio=0.5),
                        run_time=0.9,
                        rate_func=smooth,
                    )

            # Update Recording Tableau Q
            self.wait(0.5)
            r_q, c_q = chain[-1][2]
            if len(Q_data) <= r_q:
                Q_data.append([])
            Q_data[r_q].append(k + 1)

            q_box, q_text = self.create_visual_cell(r_q, c_q, k + 1, self.Q_origin, "Q")
            self.play(ShowCreation(q_box), FadeIn(q_text), run_time=0.6)

            # Cleanup highlight
            self.play(pi_mobs[k].animate.set_color(GREY), run_time=0.2)

        self.wait(2)


# =============================================================================
# 4. Inverse Scene (Recovery)
# =============================================================================


class RSKInverse(RSKBase):
    def construct(self):
        # 1. Setup Titles
        self.setup_headers("Recovering π from (P, Q)")

        # 2. Setup Layout (Strictly preserving your parameters)
        RESULT_Y = 2.0

        # Create the slots (underscores)
        slots = VGroup(
            *[Line(LEFT * 0.3, RIGHT * 0.3).set_stroke(GREY, 2) for _ in range(10)]
        )
        # Offset logic: 0.35 units below the RESULT_Y line
        slots.arrange(RIGHT, buff=0.4).move_to([0, RESULT_Y - 0.35, 0])

        # Create the "π =" label
        pi_label = (
            Text("π = ").scale(0.8).move_to([slots.get_left()[0] - 0.6, RESULT_Y, 0])
        )

        self.play(Write(pi_label), ShowCreation(slots))

        # Calculate destination points for the flying numbers
        destinations = [np.array([line.get_center()[0], RESULT_Y, 0]) for line in slots]
        final_mobs = [None] * 10

        # Setup Tableaux positions relative to the slots
        self.setup_tableaux_layout(slots)

        # 3. Draw Initial Tableaux (P and Q)
        P_input = [[1, 2, 5, 6, 7], [3, 4, 8], [9], [10]]
        Q_input = [[1, 3, 4, 6, 10], [2, 5, 8], [7], [9]]

        p_group = self.generate_tableau_group(P_input, self.P_origin, "P")
        q_group = self.generate_tableau_group(Q_input, self.Q_origin, "Q")

        # Animate the drawing gradually as requested (2 seconds)
        self.play(ShowCreation(p_group), ShowCreation(q_group), run_time=1.0)
        self.wait(1)

        # 4. Inverse Animation Logic
        P_data = deepcopy(P_input)
        Q_data = deepcopy(Q_input)
        bump_vec = 0.6 * self.BOX_SIZE * UP

        for k in range(10, 0, -1):
            # Step A: Locate and remove number k from Q
            r, c = next((r, row.index(k)) for r, row in enumerate(Q_data) if k in row)

            q_mob = self.mobs["Q"].pop(k)
            q_box = self.boxes["Q"].pop((r, c))

            self.play(
                q_mob.animate.set_color(YELLOW).scale(1.2),
                q_box.animate.set_stroke(YELLOW, 4),
                run_time=0.3,
            )
            self.play(FadeOut(q_mob), FadeOut(q_box), run_time=0.6)

            # Update Q data
            Q_data[r].remove(k)
            if not Q_data[r]:
                Q_data.pop(r)
            self.wait(0.5)

            # Step B: Identify the corresponding element in P and prepare for removal
            p_val = P_data[r][c]
            p_mob = self.mobs["P"][p_val]
            p_box = self.boxes["P"].pop((r, c))

            self.play(
                p_mob.animate.set_color(RED),
                p_box.animate.set_stroke(RED, 4),
                run_time=0.4,
            )
            self.play(FadeOut(p_box), run_time=0.4)

            # Step C: Calculate the reverse bumping path
            chain, _ = reverse_schensted(P_data, r, c)

            # Step D: Animate the bumping inside P
            curr_mob = p_mob
            for step in chain:
                tr, tc = step["target"]
                # The value currently at the target (kicked) will be bumped UP
                next_mob = self.mobs["P"][step["kicked"]]
                target_pos = self.get_pos(tr, tc, self.P_origin)

                self.play(
                    AnimationGroup(
                        curr_mob.animate.move_to(target_pos).set_color(WHITE),
                        next_mob.animate.move_to(target_pos + bump_vec).set_color(RED),
                        lag_ratio=0.4,
                    ),
                    run_time=1.0,
                )
                curr_mob = next_mob

            # Step E: Fly the ejected number to the result slot
            self.play(
                curr_mob.animate.move_to(destinations[k - 1])
                .set_color(YELLOW)
                .scale(0.9),
                run_time=0.6,
            )
            final_mobs[k - 1] = curr_mob

        # 5. Final Result Formatting
        self.wait(0.5)
        self.play(FadeOut(slots))

        pi_prefix = Text("π = (").scale(0.8)
        pi_suffix = Text(")").scale(0.8)

        # Create a final group to align parenthesis nicely
        final_group = (
            VGroup(pi_prefix, *final_mobs, pi_suffix)
            .arrange(RIGHT, buff=0.4)
            .move_to([0, RESULT_Y, 0])
        )

        self.play(
            ReplacementTransform(pi_label, pi_prefix),
            FadeIn(pi_suffix),
            *[
                mob.animate.move_to(final_group[i + 1]).set_color(WHITE)
                for i, mob in enumerate(final_mobs)
            ],
            run_time=1.2
        )

        # Restore static Tableaux for the final scene
        self.boxes = {"P": {}, "Q": {}}
        self.mobs = {"P": {}, "Q": {}}

        self.play(
            FadeIn(self.generate_tableau_group(P_input, self.P_origin, "P")),
            FadeIn(self.generate_tableau_group(Q_input, self.Q_origin, "Q")),
            run_time=1.5,
        )
        self.wait(2)
