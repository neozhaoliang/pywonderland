"use strict" ;
console.clear() ;

var container,
    renderer,
    scene,
    camera,
    controls,
    mesh,
    uniforms,
    material,
    start = Date.now(),
    fov = 30;

var canvasSize = 600;

window.addEventListener( 'load', function() {

    // grab the container from the DOM
    container = document.getElementById( "container" );

    // create a scene
    scene = new THREE.Scene();

    // create a camera the size of the browser window
    // and place it 100 units away, looking towards the center of the scene
    camera = new THREE.PerspectiveCamera(
        fov,
        1,
        0.01,
        100
    );
    camera.position.z = 5;
	
    const CIRCLE=0.0 ;
    const LINE=1.0 ;
    const END=9.0 ;
    
    // helper function returns line from two points.
    function line([a, b], [c, d]){
	return [b-d,c-a,a*d-b*c] ;
    }
    
    const config6_circles = {name: "Cheritat",
			     value: [
				 //LINE,-Math.sqrt(3),1,0,
				 LINE,...line([0,0],[1,Math.sqrt(3)]),
				 //LINE,0,-1,0,
				 LINE,...line([1,0],[0,0]),
				 CIRCLE,0.555062,-0.961395, 1*1.92279,
				 CIRCLE,16.55217328, 0, 15.91020851,
				 END, 0, 0, 0,
			     ]} ; 
    
    uniforms = {
        u_time: { type: "f", value: 1.0 },
	u_zoom: {value: 1.0},
	u_circles: config6_circles,
    };
    
    material = new THREE.ShaderMaterial( {
	uniforms: uniforms,
	vertexShader: document.getElementById( 'vertexShader' ).textContent,
	fragmentShader: document.getElementById( 'fragmentShader' ).textContent,
    } );
    
    // create a sphere and assign the material
    var radius = 1 ;
    mesh = new THREE.Mesh(
        //new THREE.IcosahedronGeometry( 20, 4 ),
	new THREE.SphereGeometry(radius, 200, 100),
        material
    );
    scene.add( mesh );
    
    var geometry = new THREE.Geometry();
    
    // create the renderer and attach it to the DOM
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(canvasSize, canvasSize);
    renderer.setPixelRatio( window.devicePixelRatio );
    
    container.appendChild( renderer.domElement );
    
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true ;
    controls.dampingFactor = 0.1 ;
    controls.maxDistance = 10 ;
    controls.minDistance = 1.01 ;
    controls.autoRotate = true ;
    
    window.addEventListener('resize', () => {
        camera.aspect = 1;
        camera.updateProjectionMatrix();
        renderer.setSize(canvasSize, canvasSize);
    }, false);
    render();
    
} );

let frame = 0 ;
function render() {   
    requestAnimationFrame( render );
    renderer.render( scene, camera );
    controls.update() ;
    const {x,y,z} = camera.position ;
    const distance = Math.sqrt(x*x+y*y+z*z)-1 ;
    controls.rotateSpeed = 0.01*distance ;
    controls.autoRotateSpeed = 0.05*distance ;
    controls.zoomSpeed = Math.min(1.0,0.5 * distance) ;
    uniforms.u_time.value = Date.now()-start ;  
    uniforms.u_zoom.value = 5/distance ;
}
