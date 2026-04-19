import streamlit as st
import streamlit.components.v1 as components

# Настройка страницы (должна быть в самом начале)
st.set_page_config(page_title="Maglev Engineering Pro", layout="wide")

st.sidebar.header("🕹️ Управление экспериментом")
speed = st.sidebar.slider("Скорость (км/ч)", 0, 600, 300)
mass = st.sidebar.slider("Масса состава (т)", 10, 100, 45)

# Расчет зазора (чисто визуальный для модели)
gap_viz = max(0.5, 10.0 - (mass / 20.0))

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; background: #0d1117; overflow: hidden; }}
        canvas {{ width: 100%; height: 100%; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0d1117);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(10, 10, 15);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        
        // Освещение
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(5, 10, 7.5);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        // Поезд (Белый обтекаемый блок)
        const trainGeo = new THREE.CapsuleGeometry(1.5, 8, 4, 16);
        const trainMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, metalness: 0.5, roughness: 0.2 }});
        const train = new THREE.Mesh(trainGeo, trainMat);
        train.rotation.z = Math.PI / 2;
        scene.add(train);

        // Рельс (Трасса)
        const railGeo = new THREE.BoxGeometry(100, 0.5, 4);
        const railMat = new THREE.MeshStandardMaterial({{ color: 0x333333 }});
        const rail = new THREE.Mesh(railGeo, railMat);
        rail.position.y = -2;
        scene.add(rail);

        function animate() {{
            requestAnimationFrame(animate);
            
            // Динамика высоты
            train.position.y = -1.5 + ({gap_viz} * 0.1);
            
            // Иллюзия движения
            rail.position.x -= {speed} * 0.001;
            if (rail.position.x < -20) rail.position.x = 0;

            controls.update();
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
