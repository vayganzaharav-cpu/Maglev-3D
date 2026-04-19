import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# Настройка страницы на всю ширину
st.set_page_config(page_title="Maglev PRO Simulator", layout="wide", initial_sidebar_state="expanded")

st.markdown("<h1 style='text-align: center; color: #00ffcc;'>🚄 Инженерный 3D-симулятор Маглева</h1>", unsafe_allow_html=True)
st.markdown("---")

# Панель управления (Слева)
with st.sidebar:
    st.header("🎛️ Панель управления")
    mass = st.slider("Масса поезда (кг)", 10, 500, 150, help="Влияет на силу тяжести")
    magnet_power = st.slider("Мощность магнитов (M)", 10, 150, 80, help="Определяет выталкивающую силу")
    speed = st.slider("Скорость (км/ч)", 0, 600, 300, help="Анимация движения")
    
    st.markdown("### Расчет в реальном времени")
    st.latex(r"d = \sqrt{\frac{k \cdot M}{m \cdot g}}")
    
# Физическое ядро (упрощенный расчет для визуализации)
k_calib = 5000
g = 9.8
force_gravity = mass * g
# Защита от деления на ноль и расчет зазора (d)
levitation_gap = np.sqrt((k_calib * magnet_power) / (force_gravity + 0.1))

# Ограничиваем высоту для красивой картинки (от 1 до 15 мм)
viz_height = max(0.5, min(15.0, levitation_gap))

# Цветовая индикация состояния
if viz_height < 2.0:
    status_color = "#ff3333" # Красный (Опасность)
    status_text = "КРИТИЧЕСКИЙ ЗАЗОР! РИСК ТРЕНИЯ"
else:
    status_color = "#00ffcc" # Зеленый (Норма)
    status_text = "СИСТЕМА СТАБИЛЬНА"

# 3D Движок (Three.js) внедренный в HTML
# Используем надежный CDN и добавляем тени, сетку и группировку объектов
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #0d1117; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        canvas {{ display: block; }}
        #hud {{
            position: absolute; top: 15px; left: 15px;
            background: rgba(13, 17, 23, 0.85); border: 1px solid {status_color};
            padding: 15px; border-radius: 8px; color: white; box-shadow: 0 0 15px {status_color}40;
        }}
        .value {{ color: {status_color}; font-weight: bold; font-size: 1.2em; }}
    </style>
</head>
<body>
    <div id="hud">
        <div style="font-size: 0.9em; color: #888;">СТАТУС: {status_text}</div>
        <hr style="border-color: #333;">
        Зазор левитации: <span class="value">{viz_height:.2f} мм</span><br>
        Масса вагона: <span class="value">{mass} кг</span><br>
        Скорость: <span class="value">{speed} км/ч</span>
    </div>

    <script>
        // Инициализация сцены
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0d1117, 0.015); // Профессиональный туман вдалеке

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(15, 10, 20);
        camera.lookAt(0, 2, 0);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true; // Включаем тени
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        // Освещение
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);

        const spotLight = new THREE.SpotLight(0xffffff, 1.5);
        spotLight.position.set(10, 30, 10);
        spotLight.castShadow = true;
        spotLight.shadow.mapSize.width = 2048;
        spotLight.shadow.mapSize.height = 2048;
        scene.add(spotLight);

        const blueLight = new THREE.PointLight(0x00ffcc, 1, 50);
        blueLight.position.set(0, 5, 0);
        scene.add(blueLight);

        // Инженерная сетка координат
        const gridHelper = new THREE.GridHelper(200, 100, 0x00ffcc, 0x444444);
        gridHelper.position.y = -2;
        gridHelper.material.opacity = 0.2;
        gridHelper.material.transparent = true;
        scene.add(gridHelper);

        // --- СОЗДАНИЕ ПУТИ (Монорельс) ---
        const trackGroup = new THREE.Group();
        
        // Главная балка
        const railGeo = new THREE.BoxGeometry(200, 2, 4);
        const railMat = new THREE.MeshStandardMaterial({{ color: 0x555555, roughness: 0.6 }});
        const rail = new THREE.Mesh(railGeo, railMat);
        rail.receiveShadow = true;
        trackGroup.add(rail);

        // Боковые магниты на рельсе (полосы)
        const magStripGeo = new THREE.BoxGeometry(200, 0.5, 0.5);
        const magStripMat = new THREE.MeshStandardMaterial({{ color: 0x222222, emissive: 0x111111 }});
        const strip1 = new THREE.Mesh(magStripGeo, magStripMat);
        strip1.position.set(0, 1, 1.8);
        const strip2 = new THREE.Mesh(magStripGeo, magStripMat);
        strip2.position.set(0, 1, -1.8);
        trackGroup.add(strip1);
        trackGroup.add(strip2);

        scene.add(trackGroup);

        // --- СОЗДАНИЕ ОДИНОЧНОГО ПОЕЗДА ---
        const trainGroup = new THREE.Group();

        // Главный корпус
        const bodyGeo = new THREE.BoxGeometry(12, 3, 5);
        const bodyMat = new THREE.MeshStandardMaterial({{ color: 0xe0e0e0, metalness: 0.8, roughness: 0.2 }});
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.position.y = 1.5;
        body.castShadow = true;
        trainGroup.add(body);

        // Кабина (стекло)
        const glassGeo = new THREE.BoxGeometry(3, 1.5, 4.5);
        const glassMat = new THREE.MeshStandardMaterial({{ color: 0x000000, metalness: 0.9, roughness: 0.1 }});
        const glass = new THREE.Mesh(glassGeo, glassMat);
        glass.position.set(4.6, 2.2, 0);
        trainGroup.add(glass);

        // Магнитные захваты (лапки, обхватывающие рельс)
        const podGeo = new THREE.BoxGeometry(10, 1.5, 1);
        const podMat = new THREE.MeshStandardMaterial({{ color: 0x333333 }});
        const podLeft = new THREE.Mesh(podGeo, podMat);
        podLeft.position.set(0, 0.5, 2.5);
        podLeft.castShadow = true;
        const podRight = new THREE.Mesh(podGeo, podMat);
        podRight.position.set(0, 0.5, -2.5);
        podRight.castShadow = true;
        trainGroup.add(podLeft);
        trainGroup.add(podRight);

        // Нижние магниты (светящиеся)
        const hoverLightGeo = new THREE.PlaneGeometry(8, 3);
        const hoverLightMat = new THREE.MeshBasicMaterial({{ color: '{status_color}', side: THREE.DoubleSide }});
        const hoverLight = new THREE.Mesh(hoverLightGeo, hoverLightMat);
        hoverLight.rotation.x = Math.PI / 2;
        hoverLight.position.y = -0.1;
        trainGroup.add(hoverLight);

        scene.add(trainGroup);

        // Анимация
        let t = 0;
        function animate() {{
            requestAnimationFrame(animate);
            
            // Физика левитации (позиция Y)
            // Добавляем микро-вибрации для реалистичности
            const baseHeight = ({viz_height} * 0.3) + 1; 
            const vibration = (Math.random() * 0.05 - 0.02) * ({mass}/500); 
            trainGroup.position.y = baseHeight + vibration;
            
            // Иллюзия движения (двигаем рельс назад)
            if ({speed} > 0) {{
                t += {speed} * 0.002;
                trackGroup.position.x = -(t % 20); // Зацикливаем движение пути
                
                // Легкий наклон поезда назад при разгоне (опционально)
                trainGroup.rotation.z = Math.min({speed} * 0.0001, 0.05);
            }} else {{
                trainGroup.rotation.z = 0;
            }}
            
            // Пульсация света левитации
            blueLight.intensity = 1 + Math.sin(Date.now() * 0.01) * 0.2;
            blueLight.color.setHex(parseInt('{status_color}'.replace('#', '0x')));

            renderer.render(scene, camera);
        }}
        
        // Адаптация под размер окна
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        animate();
    </script>
</body>
</html>
"""

# Вставка HTML блока на всю ширину
components.html(html_code, height=700)

st.markdown("### 📋 Анализ данных эксперимента")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Действующая сила тяжести (F=mg)", value=f"{force_gravity:.1f} Н")
with col2:
    st.metric(label="Подъемная сила магнитов", value=f"{magnet_power * k_calib} у.е.")
with col3:
    st.metric(label="Расчетный зазор (d)", value=f"{levitation_gap:.2f} мм")
