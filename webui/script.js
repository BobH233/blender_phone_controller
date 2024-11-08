document.addEventListener('DOMContentLoaded', function () {
    const statusDiv = document.getElementById('status');
    const requestPermissionBtn = document.getElementById('requestPermissionBtn');
    const enableSendBtn = document.getElementById('enableSendBtn');
    const disableSendBtn = document.getElementById('disableSendBtn');
    
    const wsPort = new URLSearchParams(window.location.search).get('wsport');
    const wsUrl = `wss://${window.location.hostname}:${window.location.port}`;
    const connectUrl = './ws_connect';
    const reportUrl = './ws_report';

    let lastMotionTimestamp = 0;
    let lastOrientationTimestamp = 0;
    const fpsInterval = 1000 / 60;

    
    let fake_alpha = 0;
    let fake_beta = 0;
    let fake_gamma = 0;

    let ws;
    function connectWebSocket2() {
        ws = io.connect(wsUrl, { transports: ['websocket'] });
        ws.on('connect', () => {
            statusDiv.textContent = 'WebSocket连接成功！';
            requestPermissionBtn.style.display = 'inline-block';
            requestPermissionBtn.addEventListener('click', requestSensorAccess);
        })
        ws.on('error', () => {
            statusDiv.textContent = 'WebSocket转发服务器未启动！';
            alert('WebSocket转发服务器未启动，请确保服务器正常运行。');
            console.error('连接错误:', error);
        })
    }
    

    function connectWebSocket1() {
        fetch(connectUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ port: wsPort })
        })
        .then(response => {
            if (response.ok) {
                statusDiv.textContent = 'WebSocket连接成功！';
                requestPermissionBtn.style.display = 'inline-block';
                requestPermissionBtn.addEventListener('click', requestSensorAccess);
            } else {
                throw new Error('连接失败');
            }
        })
        .catch(error => {
            statusDiv.textContent = 'WebSocket接收服务器未启动！';
            alert('WebSocket接收服务器未启动，请确保服务器正常运行。');
            console.error('连接错误:', error);
        });
    }

    let sending = true;

    function requestSensorAccess() {
        if (typeof DeviceMotionEvent.requestPermission === 'function' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            // 请求陀螺仪和姿态传感器权限
            Promise.all([
                DeviceMotionEvent.requestPermission(),
                DeviceOrientationEvent.requestPermission()
            ])
            .then(permissionStates => {
                const [motionPermission, orientationPermission] = permissionStates;
                if (motionPermission === 'granted' && orientationPermission === 'granted') {
                    window.addEventListener('devicemotion', handleMotion);
                    window.addEventListener('deviceorientation', handleOrientation);
                    requestPermissionBtn.style.display = 'none';
                    disableSendBtn.style.display = 'inline-block';
                    disableSendBtn.onclick = () => {
                        sending = false;
                        enableSendBtn.style.display = 'inline-block';
                        disableSendBtn.style.display = 'none';
                        fake_alpha = fake_beta = fake_gamma = 0;
                    }
                    enableSendBtn.onclick = () => {
                        sending = true;
                        disableSendBtn.style.display = 'inline-block';
                        enableSendBtn.style.display = 'none';
                    }
                } else {
                    statusDiv.textContent = '无法获取传感器权限！';
                }
            })
            .catch(console.error);
        } else {
            // 如果设备不需要请求权限
            window.addEventListener('devicemotion', handleMotion);
            window.addEventListener('deviceorientation', handleOrientation);
            requestPermissionBtn.style.display = 'none';
        }
    }

    let last_integral_time = 0;

    function handleMotion(event) {
        if(!sending) return;
        const currentTimestamp = Date.now();
        if (last_integral_time == 0) {
            last_integral_time = currentTimestamp;
        } else {
            let delta_time = currentTimestamp -last_integral_time;
            if (delta_time > 500) {
                // timeout
                last_integral_time = currentTimestamp;
            } else {
                fake_alpha += delta_time * event.rotationRate.alpha * 0.001;
                fake_beta += delta_time * event.rotationRate.beta * 0.001;
                fake_gamma += delta_time * event.rotationRate.gamma * 0.001;
            }
            last_integral_time = currentTimestamp;
        }

        if (currentTimestamp - lastMotionTimestamp >= fpsInterval) {
            lastMotionTimestamp = currentTimestamp;

            const gyroData = {
                x: event.rotationRate.alpha,
                y: event.rotationRate.beta,
                z: event.rotationRate.gamma
            };

            const accelData = {
                x: event.accelerationIncludingGravity.x,
                y: event.accelerationIncludingGravity.y,
                z: event.accelerationIncludingGravity.z
            };

            const fakeData = {
                fake_alpha,
                fake_beta,
                fake_gamma
            }

            const data = {
                cmd: 'update_phone_acc',
                timestamp: currentTimestamp,
                param: {
                    gyro: gyroData,
                    accel: accelData,
                    fake: fakeData
                }
            };
            ws.emit('json_data', JSON.stringify(data))
        }
    }

    function handleOrientation(event) {
        if(!sending) return;
        const currentTimestamp = Date.now();
        if (currentTimestamp - lastOrientationTimestamp >= fpsInterval) {
            lastOrientationTimestamp = currentTimestamp;

            const orientationData = {
                alpha: event.alpha,
                beta: event.beta,
                gamma: event.gamma
            };
            const data = {
                cmd: 'update_phone_pose',
                timestamp: currentTimestamp,
                param: orientationData
            };
            ws.emit('json_data', JSON.stringify(data))
        }
    }

    connectWebSocket1();
    connectWebSocket2();
});
