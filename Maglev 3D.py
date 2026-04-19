import streamlit as st
import streamlit.components.v1 as components

# Настройка страницы
st.set_page_config(page_title="Maglev 3D Simulator", layout="wide")

st.title("🚀 3D Симулятор Маглева: Эксперимент №5")
st.markdown("---")

# Боковая панель управления
with st.sidebar:
    st.header("⚙️ Настройки эксперимента")
    mass = st.slider("Масса поезда (кг)", 10, 500, 100)
    magnet_power = st.slider("Мощность магнитов (M)", 10, 100, 50)
    speed = st.slider("Целевая скорость (км/ч)", 0, 600, 250)
    
    st.info("""
    **Физика процесса:**
    Высота левитации рассчитывается в реальном времени. 
    Если масса слишком велика, магнитная подушка 'просядет'.
    """)

# Расчет высоты левитации для передачи в 3D (упрощенная модель)
# d = sqrt(k * M / F), где F = mass * g
k = 5000 
g = 9.8
required_force = mass * g
levitation_height = ( (k * magnet_power) / (required_force + 1) )**0.5
# Ограничиваем высоту для визуализации (от 2 до 40 единиц)
viz_height = max(2, min(40, levitation_height))

# HTML + Three.js Код
three_js_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #0e1117; }}
        canvas {{ width: 100%; height: 100% }}
        #info {{
            position: absolute; top: 10px; left: 10px;
            color: white; font-family: sans-serif;
            background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="info">
        Высота зазора: <span id="h_val">{viz_height:.1f}</span> мм<br>
        Скорость: <span id="s_val">{speed}</span> км/ч
    </div>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Освещение
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(5, 10, 7.5).normalize();
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        // Рельс (Монорельс)
        const trackGeo = new THREE.BoxGeometry(100, 2, 4);
        const trackMat = new THREE.MeshPhongMaterial({{ color: 0x444444 }});
        const track = new THREE.Mesh(trackGeo, trackMat);
        scene.add(track);

        // Поезд (Футуристичный капсульный дизайн)
        const trainGeo = new THREE.CapsuleGeometry(1.5, 6, 4, 16);
        trainGeo.rotateZ(Math.PI / 2);
        const trainMat = new THREE.MeshPhongMaterial({{ color: 0x00ffcc, emissive: 0x112222 }});
        const train = new THREE.Mesh(trainGeo, trainMat);
        scene.add(train);

        camera.position.set(10, 10, 15);
        camera.lookAt(0, 0, 0);

        let t = 0;
        function animate() {{
            requestAnimationFrame(animate);
            
            // Анимация левитации (высота передается из Python)
            const targetY = {viz_height} / 5; // Масштабирование для 3D сцены
            train.position.y = targetY + Math.sin(Date.now() * 0.002) * 0.1; // Легкое покачивание
            
            // Анимация движения (зависит от скорости)
            t += {speed} * 0.0001;
            track.position.x = -( (t * 50) % 100 ) + 50;
            
            // Создаем копию рельса для бесконечного пути
            const track2 = track.clone();
            track2.position.x = track.position.x - 100;
            
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

# Внедрение 3D компонента
components.html(three_js_code, height=600)

# Дополнительная информация под моделью
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Анализ стабильности")
    if viz_height < 5:
        st.warning("⚠️ ОПАСНО: Критически малый зазор. Высокий риск трения.")
    elif speed > 400 and viz_height < 10:
        st.error("❌ СХОД: Центробежные силы на такой скорости опрокинут состав.")
    else:
        st.success("✅ СТАБИЛЬНО: Система удерживает равновесие.")

with col2:
    st.latex(r"d \approx \sqrt{\frac{k \cdot M}{m \cdot g}}")
    st.write(f"Текущий расчетный зазор: **{levitation_height:.2f} мм**")
