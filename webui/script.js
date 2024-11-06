document.addEventListener('DOMContentLoaded', function () {
    const statusDiv = document.getElementById('status');
    const requestPermissionBtn = document.getElementById('requestPermissionBtn');
    
    const wsPort = new URLSearchParams(window.location.search).get('wsport');
    const connectUrl = './ws_connect';
    const reportUrl = './ws_report';

    function connectWebSocket() {
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
            statusDiv.textContent = 'WebSocket服务器未启动！';
            alert('WebSocket服务器未启动，请确保服务器正常运行。');
            console.error('连接错误:', error);
        });
    }

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

    function handleMotion(event) {
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

        const data = {
            cmd: 'update_phone_acc',
            param: {
                gyro: gyroData,
                accel: accelData
            }
        };

        fetch(reportUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(console.error);
    }

    function handleOrientation(event) {
        const orientationData = {
            alpha: event.alpha,
            beta: event.beta,
            gamma: event.gamma
        };
        const data = {
            cmd: 'update_phone_pose',
            param: orientationData
        };

        fetch(reportUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(console.error);
    }

    connectWebSocket();
});
