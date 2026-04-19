import streamlit as st
import streamlit.components.v1 as components
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #0d1117; font-family: sans-serif; }}
        canvas {{ display: block; }}
        #hud {{
            position: absolute; top: 15px; left: 15px;
            background: rgba(13, 17, 23, 0.85); border: 1px solid {status_color};
            padding: 15px; border-radius: 8px; color: white;
            pointer-events: none; z-index: 100;
        }}
        .value {{ color: {status_color}; font-weight: bold; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div id="hud">
        <div style="font-size: 0.8em; color: #888;">СТАТУС: {status_text}</div>
        Зазор: <span class="value">{viz_height:.2f} мм</span><br>
        Скорость: <span class="value">{speed} км/ч</span>
    </div>

    <script>
        // --- БАЗОВАЯ НАСТРОЙКА ---
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0d1117, 0.01); // Туман для бесконечной трассы

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(15, 8, 20); // Начальная позиция камеры

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true; // Тени
        document.body.appendChild(renderer.domElement);

        // --- ДОБАВЛЯЕМ ВРАЩЕНИЕ КАМЕРЫ (OrbitControls) ---
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; // Плавное замедление при вращении
        controls.dampingFactor = 0.05;
        controls.minDistance = 5;      // Минимальное приближение
        controls.maxDistance = 100;    // Максимальное отдаление
        controls.target.set(0, 2, 0);  // Камера смотрит на поезд

        // --- ОСВЕЩЕНИЕ ---
        scene.add(new THREE.AmbientLight(0xffffff, 0.4));
        const sun = new THREE.DirectionalLight(0xffffff, 1);
        sun.position.set(10, 20, 10);
        sun.castShadow = true;
        scene.add(sun);

        // --- СОЗДАНИЕ БЕСКОНЕЧНОЙ ТРАССЫ (ЭСТАКАДЫ) ---
        const trackGroup = new THREE.Group();
        
        // Материалы трассы
        const concreteMat = new THREE.MeshStandardMaterial({{ color: 0x444444, roughness: 0.9 }});
        const railMat = new THREE.MeshStandardMaterial({{ color: 0x111111, metalness: 0.8 }});

        // Создаем сегмент трассы (который будем клонировать)
        function createTrackSegment(xOffset) {{
            const segment = new THREE.Group();
            
            // Основная бетонная балка
            const beamGeo = new THREE.BoxGeometry(20, 1.5, 4);
            const beam = new THREE.Mesh(beamGeo, concreteMat);
            beam.receiveShadow = true;
            segment.add(beam);

            // Магнитные рельсы (полосы)
            const railGeo = new THREE.BoxGeometry(20, 0.3, 0.6);
            const rail1 = new THREE.Mesh(railGeo, railMat);
            rail1.position.set(0, 0.9, 1.7);
            const rail2 = rail1.clone();
            rail2.position.set(0, 0.9, -1.7);
            segment.add(rail1);
            segment.add(rail2);

            // Опора эстакады (столб)
            const pillarGeo = new THREE.CylinderGeometry(1, 1.5, 15, 6);
            const pillar = new THREE.Mesh(pillarGeo, concreteMat);
            pillar.position.set(0, -8, 0);
            pillar.receiveShadow = true;
            segment.add(pillar);

            segment.position.x = xOffset;
            return segment;
        }}

        // Генерируем 10 сегментов вперед и назад
        for (let i = -5; i < 15; i++) {{
            trackGroup.add(createTrackSegment(i * 20));
        }}
        scene.add(trackGroup);

        // --- СОЗДАНИЕ ОБТЕКАЕМОГО ПОЕЗДА (PRO ВИД) ---
        const trainGroup = new THREE.Group();
        
        // Материал корпуса (металл с отсветом)
        const bodyMat = new THREE.MeshStandardMaterial({{ 
            color: 0xffffff, 
            metalness: 0.9, 
            roughness: 0.1,
            emissive: 0x111111
        }});

        // 1. Главный цилиндрический корпус
        const bodyGeo = new THREE.CylinderGeometry(1.8, 1.8, 12, 32);
        bodyGeo.rotateZ(Math.PI / 2); // Кладем цилиндр на бок
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.position.y = 1.8;
        body.castShadow = true;
        trainGroup.add(body);

        // 2. Обтекаемый нос (Капсула)
        const noseGeo = new THREE.CapsuleGeometry(1.8, 3, 16, 32);
        noseGeo.rotateZ(Math.PI / 2);
        const nose = new THREE.Mesh(noseGeo, bodyMat);
        nose.position.set(6, 1.8, 0); // Ставим впереди корпуса
        nose.castShadow = true;
        trainGroup.add(nose);

        // 3. Кабина водителя (темное стекло)
        const glassMat = new THREE.MeshStandardMaterial({{ color: 0x010101, metalness: 1, roughness: 0 }});
        const glassGeo = new THREE.CapsuleGeometry(1.2, 2, 8, 16);
        glassGeo.rotateZ(Math.PI / 2);
        const glass = new THREE.Mesh(glassGeo, glassMat);
        glass.position.set(6.5, 2.2, 0); // На носу
        trainGroup.add(glass);

        // 4. Боковые обтекатели магнитов (юбка)
        const skirtGeo = new THREE.BoxGeometry(15, 1.2, 5.2);
        const skirtMat = new THREE.MeshStandardMaterial({{ color: 0x222222 }});
        const skirt = new THREE.Mesh(skirtGeo, skirtMat);
        skirt.position.set(1, 0.6, 0);
        trainGroup.add(skirt);

        // 5. Нижнее свечение левитации
        const lightGeo = new THREE.PlaneGeometry(12, 4);
        const lightMat = new THREE.MeshBasicMaterial({{ color: '{status_color}', transparent: true, opacity: 0.7 }});
        const lightPlane = new THREE.Mesh(lightGeo, lightMat);
        lightPlane.rotation.x = -Math.PI / 2;
        lightPlane.position.y = -0.1;
        trainGroup.add(lightPlane);

        scene.add(trainGroup);

        // --- АНИМАЦИЯ И ФИЗИКА ---
        let clock = new THREE.Clock();

        function animate() {{
            requestAnimationFrame(animate);
            let delta = clock.getDelta();
            
            // Необходим для плавного damping в OrbitControls
            controls.update(); 

            // 1. Физика левитации (позиция Y)
            const targetY = ({viz_height} * 0.2) + 0.5; // Масштабирование зазора
            // Плавное изменение высоты (сглаживание)
            trainGroup.position.y = THREE.MathUtils.lerp(trainGroup.position.y, targetY, 0.1);
            
            // 2. Иллюзия движения по трассе
            if ({speed} > 0) {{
                // Сдвигаем всю группу трассы назад
                trackGroup.position.x -= {speed} * 0.005;
                
                // Если сегмент ушел далеко назад, перекидываем его вперед (бесконечная петля)
                trackGroup.children.forEach(segment => {{
                    // Получаем мировую позицию сегмента
                    let worldPos = new THREE.Vector3();
                    segment.getWorldPosition(worldPos);
                    
                    if (worldPos.x < -40) {{
                        segment.position.x += 20 * 20; // Перенос на 20 сегментов вперед
                    }}
                }});
            }}
            
            // 3. Визуальные эффекты
            // Изменяем цвет свечения в зависимости от статуса
            lightPlane.material.color.setHex(parseInt('{status_color}'.replace('#', '0x')));
            
            renderer.render(scene, camera);
        }}
        
        animate();

        // Адаптация под размер окна
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""
