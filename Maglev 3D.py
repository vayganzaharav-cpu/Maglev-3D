import streamlit as st
import streamlit.components.v1 as components

# Настройка страницы
st.set_page_config(page_title="Maglev Pro Simulator", layout="wide")

# Заголовок
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>🚄 Инженерный 3D-симулятор Маглева</h1>", unsafe_allow_html=True)

# Боковая панель управления
st.sidebar.header("🕹️ Настройки эксперимента")
mass = st.sidebar.slider("Масса поезда (кг)", 200, 1000, 450)
power = st.sidebar.slider("Мощность магнитов (кВт)", 50, 300, 180)
speed = st.sidebar.slider("Целевая скорость (км/ч)", 0, 600, 350)

# Физический расчет зазора (d)
# Используем упрощенную формулу для демонстрации стабильности
levitation_gap = (power / (mass * 0.098)) * 0.5
viz_height = max(0.5, min(15.0, levitation_gap))

# Цветовая индикация состояния
if viz_height < 3.0:
    status_color = "#ff3333" # Красный (Опасно)
    status_text = "ВНИМАНИЕ: КРИТИЧЕСКИЙ ЗАЗОР"
else:
    status_color = "#00ffcc" # Бирюзовый (Стабильно)
    status_text = "СИСТЕМА СТАБИЛЬНА"

# HTML + JavaScript (Three.js) блок
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; background: #0d1117; overflow: hidden; }}
        #ui-overlay {{
            position: absolute; top: 20px; left: 20px;
            color: white; font-family: 'Segoe UI', sans-serif;
            background: rgba(13, 17, 23, 0.8); padding: 15px;
            border-radius: 10px; border: 1px solid {status_color};
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div id="ui-overlay">
        <div style="color: {status_color}; font-weight: bold;">{status_text}</div>
        <div style="font-size: 24px; margin-top: 5px;">{viz_height:.2f} мм</div>
        <div style="color: #888; font-size: 12px;">Высота левитации</div>
    </div>

    <script>
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0d1117, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(15, 10, 25);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Свет
        scene.add(new THREE.AmbientLight(0xffffff, 0.4));
        const spot = new THREE.SpotLight(0xffffff, 1.2);
        spot.position.set(20, 40, 20);
        spot.castShadow = true;
        scene.add(spot);

        // Трасса (Эстакада)
        const trackGroup = new THREE.Group();
        const createTrack = (x) => {{
            const g = new THREE.Group();
            const beam = new THREE.Mesh(
                new THREE.BoxGeometry(20, 1, 5),
                new THREE.MeshStandardMaterial({{ color: 0x222222 }})
            );
            beam.receiveShadow = true;
            const pillar = new THREE.Mesh(
                new THREE.CylinderGeometry(1, 1.5, 20),
                new THREE.MeshStandardMaterial({{ color: 0x1a1a1a }})
            );
            pillar.position.y = -10.5;
            g.add(beam, pillar);
            g.position.x = x;
            return g;
        }};
        
        for(let i = -5; i < 15; i++) trackGroup.add(createTrack(i * 20));
        scene.add(trackGroup);

        // --- РЕАЛИСТИЧНЫЙ ПОЕЗД ---
        const train = new THREE.Group();
        const bodyMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, metalness: 0.9, roughness: 0.1 }});
        
        // Обтекаемый корпус
        const body = new THREE.Mesh(new THREE.CapsuleGeometry(1.8, 12, 4, 32), bodyMat);
        body.rotation.z = Math.PI / 2;
        body.castShadow = true;
        train.add(body);

        // Кабина (Черное стекло)
        const glass = new THREE.Mesh(
            new THREE.CapsuleGeometry(1.3, 2, 4, 16),
            new THREE.MeshStandardMaterial({{ color: 0x000000, metalness: 1 }})
        );
        glass.rotation.z = Math.PI / 2;
        glass.position.set(6.5, 0.6, 0);
        train.add(glass);

        // Боковые магниты (светящиеся)
        const glowMat = new THREE.MeshBasicMaterial({{ color: '{status_color}', transparent: true, opacity: 0.6 }});
        const glow = new THREE.Mesh(new THREE.BoxGeometry(14, 0.2, 5.2), glowMat);
        glow.position.y = -1.6;
        train.add(glow);

        scene.add(train);

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();

            // Динамика
            train.position.y = 1.8 + ({viz_height} * 0.1);
            
            if ({speed} > 0) {{
                trackGroup.position.x -= {speed} * 0.002;
                if (trackGroup.position.x < -20) trackGroup.position.x = 0;
                train.rotation.x = Math.sin(Date.now() * 0.005) * 0.01; // Легкая качка
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

# Отображение 3D компонента
components.html(html_code, height=700)

# Текстовый блок анализа
st.markdown("---")
st.markdown("### 📊 Анализ динамической стабильности")
st.info("Стабильность системы не является пассивной. Даже при точных параметрах внешние возмущения или задержки в управлении могут привести к заземлению или сходу с рельсов.")

col1, col2 = st.columns(2)
col1.metric("Текущий зазор", f"{viz_height:.2f} мм", delta=f"{viz_height - 5:.1f} мм")
col2.metric("Подъемная сила", f"{power * 10} Н")
