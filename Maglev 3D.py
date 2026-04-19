import streamlit as st
import streamlit.components.v1 as components

# 1. Настройка страницы
st.set_page_config(page_title="Maglev Pro 3D", layout="wide")

st.sidebar.header("🕹️ Управление симуляцией")
speed = st.sidebar.slider("Скорость поезда (км/ч)", 0, 600, 300)
levitation = st.sidebar.slider("Высота левитации (мм)", 0, 20, 10)

# Цвет статуса (меняется на красный, если зазор слишком мал)
status_color = "#00ffcc" if levitation > 2 else "#ff3333"

# 2. HTML + JavaScript (Three.js)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; background: #0d1117; overflow: hidden; }}
        #info {{
            position: absolute; top: 10px; left: 10px;
            color: {status_color}; font-family: monospace;
            background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px;
            border: 1px solid {status_color};
        }}
    </style>
</head>
<body>
    <div id="info">SPEED: {speed} km/h | GAP: {levitation} mm</div>
    <script>
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0d1117, 0.01);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
        camera.position.set(15, 8, 20);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        // Вращение камеры мышкой
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Свет
        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(10, 20, 10);
        light.castShadow = true;
        scene.add(light);

        // --- ТРАССА (ЭСТАКАДА) ---
        const trackGroup = new THREE.Group();
        function createSegment(x) {{
            const group = new THREE.Group();
            // Балка
            const beam = new THREE.Mesh(
                new THREE.BoxGeometry(20, 1.5, 4),
                new THREE.MeshStandardMaterial({{color: 0x333333}})
            );
            beam.receiveShadow = true;
            group.add(beam);
            // Опора
            const pillar = new THREE.Mesh(
                new THREE.CylinderGeometry(0.8, 1.2, 15),
                new THREE.MeshStandardMaterial({{color: 0x222222}})
            );
            pillar.position.y = -8;
            group.add(pillar);
            group.position.x = x;
            return group;
        }}
        for(let i=-5; i<15; i++) trackGroup.add(createSegment(i*20));
        scene.add(trackGroup);

        // --- ПОЕЗД ---
        const train = new THREE.Group();
        const mat = new THREE.MeshStandardMaterial({{color: 0xffffff, metalness: 0.8, roughness: 0.2}});
        
        // Корпус
        const body = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 12, 32), mat);
        body.rotation.z = Math.PI/2;
        train.add(body);
        
        // Нос (капсула)
        const nose = new THREE.Mesh(new THREE.CapsuleGeometry(1.5, 3, 16, 32), mat);
        nose.rotation.z = Math.PI/2;
        nose.position.x = 6;
        train.add(nose);

        // Стекло кабины
        const glass = new THREE.Mesh(
            new THREE.CapsuleGeometry(1.1, 2, 8, 16),
            new THREE.MeshStandardMaterial({{color: 0x000000, metalness: 1}})
        );
        glass.rotation.z = Math.PI/2;
        glass.position.set(6.5, 0.5, 0);
        train.add(glass);

        train.position.y = 2;
        scene.add(train);

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            
            // Левитация (высота)
            train.position.y = 1.8 + ({levitation} * 0.05);
            
            // Движение (сдвиг трассы)
            if({speed} > 0) {{
                trackGroup.position.x -= {speed} * 0.001;
                if(trackGroup.position.x < -20) trackGroup.position.x = 0;
            }}
            
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""

components.html(html_code, height=600)
