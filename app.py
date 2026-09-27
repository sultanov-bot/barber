import socket
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Хранилище бронирований
booked_slots = [
    {"master": "Рамазан", "date": "2026-09-27", "time": "11:00"},
    {"master": "Адилет", "date": "2026-09-27", "time": "14:30"},
    {"master": "Эрбол", "date": "2026-09-27", "time": "16:00"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADAS Barbershop — NO RISK NO STYLE</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Montserrat', 'Segoe UI', sans-serif;
            user-select: none;
        }

        body {
            background-color: #030304;
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow-x: hidden;
            position: relative;
        }

        .royal-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 50% 25%, #1c170b 0%, #050507 70%, #000000 100%);
            z-index: 0;
        }

        #star-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            pointer-events: none;
        }

        .container {
            position: relative;
            z-index: 2;
            background: rgba(10, 10, 13, 0.93);
            backdrop-filter: blur(22px);
            border: 1px solid rgba(212, 175, 55, 0.4);
            padding: 40px 28px 32px 28px;
            border-radius: 22px;
            box-shadow: 0 25px 70px rgba(0, 0, 0, 0.98), 0 0 45px rgba(212, 175, 55, 0.15);
            width: 100%;
            max-width: 470px;
            text-align: center;
        }

        .crown-icon {
            font-size: 36px;
            margin-bottom: 2px;
            display: inline-block;
            filter: drop-shadow(0 0 12px rgba(212, 175, 55, 0.9));
            animation: floatCrown 3s infinite alternate ease-in-out;
        }

        @keyframes floatCrown {
            0% { transform: translateY(0) scale(1); }
            100% { transform: translateY(-6px) scale(1.06); }
        }

        .slogan {
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 4px;
            color: #d4af37;
            text-transform: uppercase;
            margin-bottom: 12px;
            text-shadow: 0 0 12px rgba(212, 175, 55, 0.6);
        }

        .brand-title {
            font-size: 48px;
            font-weight: 900;
            letter-spacing: 7px;
            background: linear-gradient(135deg, #ffffff 20%, #d4af37 80%, #aa7c11 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            margin-bottom: 2px;
        }

        .subtitle {
            color: #777;
            font-size: 10px;
            margin-bottom: 25px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .form-group {
            margin-bottom: 16px;
            text-align: left;
            position: relative;
        }

        label {
            display: block;
            margin-bottom: 6px;
            color: #bbb;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        input, select {
            width: 100%;
            padding: 14px 16px;
            background: #111114;
            border: 1px solid #282830;
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
        }

        input:focus, select:focus {
            border-color: #d4af37;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.35);
            background: #16161c;
        }

        .time-row {
            display: flex;
            gap: 12px;
        }

        .status-container {
            margin: 18px 0;
            padding: 12px 14px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(212, 175, 55, 0.25);
            border-radius: 10px;
            text-align: left;
        }

        .status-header {
            font-size: 11px;
            font-weight: 700;
            color: #2ecc71;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .time-info {
            font-size: 10px;
            color: #d4af37;
            font-weight: bold;
        }

        .date-alert {
            display: none;
            margin-top: 8px;
            padding: 8px 10px;
            background: rgba(231, 76, 60, 0.15);
            border: 1px solid rgba(231, 76, 60, 0.6);
            border-radius: 8px;
            color: #ff5252;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            box-shadow: 0 0 12px rgba(255, 82, 82, 0.4);
            animation: alertPulse 1.5s infinite alternate;
        }

        @keyframes alertPulse {
            0% { opacity: 0.8; box-shadow: 0 0 8px rgba(255, 82, 82, 0.3); }
            100% { opacity: 1; box-shadow: 0 0 16px rgba(255, 82, 82, 0.7); }
        }

        .btn-submit {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #25D366, #128C7E);
            border: none;
            border-radius: 10px;
            color: #fff;
            font-weight: 800;
            font-size: 15px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.3s;
            margin-top: 8px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 211, 102, 0.4);
        }

        .contact-info {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }

        .contact-info a {
            color: #25D366;
            text-decoration: none;
            font-weight: bold;
        }

        .emoji-pop {
            position: fixed;
            pointer-events: none;
            font-size: 28px;
            z-index: 9999;
            animation: popAndFade 1s forwards ease-out;
        }

        @keyframes popAndFade {
            0% { opacity: 1; transform: translate(-50%, -50%) scale(0.5); }
            50% { transform: translate(-50%, -120px) scale(1.4); }
            100% { opacity: 0; transform: translate(-50%, -180px) scale(1); }
        }
    </style>
</head>
<body>

    <div class="royal-bg"></div>
    <canvas id="star-canvas"></canvas>

    <div class="container">
        <div class="crown-icon">👑</div>
        <div class="slogan">NO RISK NO STYLE 💈</div>

        <div class="brand-title">ADAS</div>
        <div class="subtitle">BARBERSHOP • ROYAL BOOKING</div>

        <form id="bookingForm">
            <div class="form-group">
                <label for="name">Ваше имя</label>
                <input type="text" id="name" placeholder="Введите ваше имя" required>
            </div>

            <div class="form-group">
                <label for="phone">Номер телефона (WhatsApp)</label>
                <input type="tel" id="phone" placeholder="+996 000 000 000" required>
            </div>

            <div class="form-group">
                <label for="master">Выберите мастера</label>
                <select id="master" required>
                    <option value="">-- Выберите мастера --</option>
                    <option value="Рамазан">Рамазан 💈</option>
                    <option value="Адилет">Адилет ✂️</option>
                    <option value="Эрбол">Эрбол 👑</option>
                </select>
            </div>

            <div class="form-group">
                <label for="service">Выберите услугу</label>
                <select id="service" required>
                    <option value="">-- Прайс-лист --</option>
                    <option value="Мужская стрижка (500 сом)">Мужская стрижка — 500 сом</option>
                    <option value="Детская стрижка (400 сом)">Детская стрижка — 400 сом</option>
                    <option value="Борода (300 сом)">Борода — 300 сом</option>
                    <option value="Стрижка + борода (700 сом)">Стрижка + борода — 700 сом</option>
                    <option value="Укладка (200 сом)">Укладка — 200 сом</option>
                    <option value="Под машинкой (300 сом)">Под машинкой — 300 сом</option>
                    <option value="Чистка лица (400 сом)">Чистка лица — 400 сом</option>
                    <option value="Чистка лица + стрижка (800 сом)">Чистка лица + стрижка — 800 сом</option>
                </select>
            </div>

            <div class="time-row">
                <div class="form-group" style="flex: 1;">
                    <label for="date">Дата</label>
                    <input type="date" id="date" required>
                </div>
                <div class="form-group" style="flex: 1;">
                    <label for="time">Время (10:00 - 22:00)</label>
                    <select id="time" required>
                        <option value="">-- Время --</option>
                    </select>
                </div>
            </div>

            <div class="date-alert" id="dateAlert">
                🔴 ПРОШЛАЯ ДАТА НЕДОСТУПНА! ВЫБЕРИТЕ СЕГОДНЯ ИЛИ БУДУЩУЮ ДАТУ
            </div>

            <div class="status-container">
                <div class="status-header">
                    <span>🟢 Свободные слоты</span>
                    <span class="time-info" id="kgTimeLabel">Бишкек: --:--</span>
                </div>
            </div>

            <button type="submit" class="btn-submit" id="submitBtn">
                Записаться через WhatsApp
            </button>
        </form>

        <div class="contact-info">
            WhatsApp: <a href="https://wa.me/996551009696" target="_blank">+996 551 009 696</a>
        </div>
    </div>

    <script>
        let serverBookedSlots = {{ booked_slots|tojson }};

        const dateInput = document.getElementById('date');
        const dateAlert = document.getElementById('dateAlert');

        function getKGTime() {
            const now = new Date();
            const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
            return new Date(utc + (3600000 * 6));
        }

        const kgToday = getKGTime();
        const todayStr = kgToday.toISOString().split('T')[0];
        dateInput.min = todayStr;
        dateInput.value = todayStr;

        function updateKGTimeDisplay() {
            const kgDate = getKGTime();
            const h = String(kgDate.getHours()).padStart(2, '0');
            const m = String(kgDate.getMinutes()).padStart(2, '0');
            document.getElementById('kgTimeLabel').textContent = `Бишкек: ${h}:${m}`;
        }
        setInterval(updateKGTimeDisplay, 1000);
        updateKGTimeDisplay();

        function updateTimeSlots() {
            const timeSelect = document.getElementById('time');
            timeSelect.innerHTML = '<option value="">-- Время --</option>';

            const selectedDate = dateInput.value;
            const selectedMaster = document.getElementById('master').value;
            const kgNow = getKGTime();

            if (selectedDate < todayStr) {
                dateAlert.style.display = 'block';
                dateInput.value = todayStr;
                return;
            } else {
                dateAlert.style.display = 'none';
            }

            const isToday = (selectedDate === todayStr);
            const currentHour = kgNow.getHours();
            const currentMin = kgNow.getMinutes();

            for (let hour = 10; hour <= 22; hour++) {
                for (let min of ['00', '30']) {
                    if (hour === 22 && min === '30') continue;

                    const timeStr = `${hour}:${min}`;
                    const opt = document.createElement('option');
                    opt.value = timeStr;

                    const hNum = parseInt(hour);
                    const mNum = parseInt(min);

                    let isPast = false;
                    if (isToday) {
                        if (hNum < currentHour || (hNum === currentHour && mNum <= currentMin)) {
                            isPast = true;
                        }
                    }

                    // Проверка на бронь
                    const isBooked = serverBookedSlots.some(s => 
                        s.date === selectedDate && 
                        s.time === timeStr && 
                        (selectedMaster === "" || s.master === selectedMaster)
                    );

                    if (isPast) {
                        opt.textContent = `${timeStr} (🔴 Прошло)`;
                        opt.disabled = true;
                        opt.style.color = '#e74c3c';
                    } else if (isBooked) {
                        opt.textContent = `${timeStr} (🔴 Занято)`;
                        opt.disabled = true;
                        opt.style.color = '#e74c3c';
                    } else {
                        opt.textContent = `${timeStr} (🟢 Свободно)`;
                        opt.style.color = '#2ecc71';
                    }

                    timeSelect.appendChild(opt);
                }
            }
        }

        dateInput.addEventListener('change', updateTimeSlots);
        document.getElementById('master').addEventListener('change', updateTimeSlots);
        updateTimeSlots();

        const emojis = ['👑', '💈', '✂️', '🔥', '⭐', '✨'];
        document.addEventListener('click', (e) => {
            const emoji = document.createElement('div');
            emoji.className = 'emoji-pop';
            emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            emoji.style.left = e.clientX + 'px';
            emoji.style.top = e.clientY + 'px';
            document.body.appendChild(emoji);
            setTimeout(() => emoji.remove(), 1000);
        });

        const canvas = document.getElementById('star-canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const mouse = { x: -1000, y: -1000, radius: 150 };
        window.addEventListener('mousemove', (e) => { mouse.x = e.x; mouse.y = e.y; });
        window.addEventListener('touchmove', (e) => {
            if (e.touches.length > 0) {
                mouse.x = e.touches[0].clientX;
                mouse.y = e.touches[0].clientY;
            }
        });

        class Particle {
            constructor() { this.reset(); }
            reset() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2.5 + 1;
                this.vx = (Math.random() - 0.5) * 1.2;
                this.vy = (Math.random() - 0.5) * 1.2;
                this.alpha = Math.random() * 0.7 + 0.3;
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = '#d4af37';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) this.reset();

                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < mouse.radius) {
                    let force = (mouse.radius - dist) / mouse.radius;
                    this.x -= (dx / dist) * force * 4;
                    this.y -= (dy / dist) * force * 4;
                }
            }
        }

        const particles = [];
        for (let i = 0; i < 90; i++) particles.push(new Particle());

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
                for (let j = i + 1; j < particles.length; j++) {
                    let dx = particles[i].x - particles[j].x;
                    let dy = particles[i].y - particles[j].y;
                    let dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 90) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(212, 175, 55, ${0.35 * (1 - dist / 90)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();

        document.getElementById('bookingForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value;
            const phone = document.getElementById('phone').value;
            const master = document.getElementById('master').value;
            const service = document.getElementById('service').value;
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;

            // Отправка данных бронирования на сервер
            try {
                await fetch('/api/book', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ master, date, time })
                });
            } catch (err) {}

            const text = `NO RISK NO STYLE 💈%0A` +
                         `Здравствуйте! Я хочу записаться в *ADAS Barbershop*.%0A%0A` +
                         `👤 *Имя:* ${name}%0A` +
                         `📞 *Телефон:* ${phone}%0A` +
                         `💈 *Мастер:* ${master}%0A` +
                         `✂️ *Услуга:* ${service}%0A` +
                         `📅 *Дата:* ${date}%0A` +
                         `⏰ *Время:* ${time}`;

            window.open(`https://wa.me/996551009696?text=${text}`, '_blank');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, booked_slots=booked_slots)

@app.route('/api/book', methods=['POST'])
def book():
    data = request.json
    master = data.get('master')
    date = data.get('date')
    time = data.get('time')
    if master and date and time:
        booked_slots.append({"master": master, "date": date, "time": time})
    return jsonify({"status": "success"})

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    local_ip = get_ip()
    print("\n" + "="*50)
    print("🔥 ADAS BARBERSHOP ЗАПУЩЕН! 🔥")
    print(f"👉 На компьютере откройте: http://127.0.0.1:5000")
    print(f"📱 На ТЕЛЕФОНЕ откройте:  http://{local_ip}:5000")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)