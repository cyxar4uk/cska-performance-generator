import React, { useState, useEffect } from 'react';
import './PhoneDemo.css';

const PhoneDemo = ({ seatColors, seats }) => {
  const [phones, setPhones] = useState([
    { id: 1, sector: null, color: [255, 0, 0], active: false },
    { id: 2, sector: null, color: [0, 255, 0], active: false },
    { id: 3, sector: null, color: [0, 0, 255], active: false }
  ]);

  const [selectedPhone, setSelectedPhone] = useState(null);
  const [availableSectors, setAvailableSectors] = useState([]);

  useEffect(() => {
    if (seats && seats.length > 0) {
      const sectors = [...new Set(seats.map(s => s.sector).filter(Boolean))];
      setAvailableSectors(sectors);
    }
  }, [seats]);

  useEffect(() => {
    if (Object.keys(seatColors).length > 0) {
      setPhones(prev => prev.map(phone => {
        if (phone.sector) {
          const sectorSeats = seats.filter(s => s.sector === phone.sector);
          if (sectorSeats.length > 0) {
            const randomSeat = sectorSeats[Math.floor(Math.random() * sectorSeats.length)];
            const color = seatColors[String(randomSeat.id)] || [255, 255, 255];
            return { ...phone, color, active: true };
          }
        }
        return phone;
      }));
    }
  }, [seatColors, seats]);

  const assignSectorToPhone = (phoneId, sector) => {
    setPhones(prev => prev.map(phone =>
      phone.id === phoneId ? { ...phone, sector, active: true } : phone
    ));
  };

  const simulateFlashlight = (phoneId) => {
    const phone = phones.find(p => p.id === phoneId);
    if (!phone || !phone.active) return;

    const colors = [
      phone.color,
      [255, 255, 255],
      phone.color,
      [0, 0, 0],
      phone.color
    ];

    let index = 0;
    const interval = setInterval(() => {
      if (index >= colors.length) {
        clearInterval(interval);
        return;
      }
      setPhones(prev => prev.map(p =>
        p.id === phoneId ? { ...p, color: colors[index] } : p
      ));
      index++;
    }, 300);
  };

  return (
    <div className="phone-demo">
      <div className="demo-header">
        <h2>📱 Демонстрация на 3 телефонах</h2>
        <p>Симуляция работы перформанса на устройствах болельщиков</p>
      </div>

      <div className="phones-container">
        {phones.map(phone => (
          <div key={phone.id} className="phone-wrapper">
            <div className={`phone ${phone.active ? 'active' : ''}`}>
              <div className="phone-notch"></div>
              <div
                className="phone-screen"
                style={{
                  backgroundColor: phone.active
                    ? `rgb(${phone.color[0]}, ${phone.color[1]}, ${phone.color[2]})`
                    : '#1a1a1a'
                }}
              >
                {phone.active ? (
                  <div className="screen-content">
                    <div className="app-header">
                      <span className="app-logo">⚽ ЦСКА</span>
                      <span className="battery">🔋 95%</span>
                    </div>
                    <div className="color-display">
                      <div className="color-info">
                        <div className="sector-badge">{phone.sector}</div>
                        <div className="rgb-values">
                          RGB: {phone.color[0]}, {phone.color[1]}, {phone.color[2]}
                        </div>
                      </div>
                    </div>
                    <div className="app-footer">
                      <button
                        className="test-btn"
                        onClick={() => simulateFlashlight(phone.id)}
                      >
                        Тест
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="screen-inactive">
                    <div className="inactive-icon">📱</div>
                    <div className="inactive-text">Ожидание</div>
                  </div>
                )}
              </div>
              <div className="phone-button"></div>
            </div>

            <div className="phone-controls">
              <label>Телефон #{phone.id}</label>
              <select
                value={phone.sector || ''}
                onChange={(e) => assignSectorToPhone(phone.id, e.target.value)}
                className="sector-select"
              >
                <option value="">Выбрать сектор</option>
                {availableSectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
            </div>
          </div>
        ))}
      </div>

      <div className="demo-info">
        <div className="info-card">
          <h3>Как это работает</h3>
          <ol>
            <li>Выберите сектор для каждого телефона</li>
            <li>Сгенерируйте перформанс в главном окне</li>
            <li>Телефоны автоматически получат цвета своих мест</li>
            <li>Нажмите "Тест" для симуляции мигания</li>
          </ol>
        </div>

        <div className="info-card stats">
          <h3>Статистика</h3>
          <div className="stat-row">
            <span>Активных телефонов:</span>
            <strong>{phones.filter(p => p.active).length} / 3</strong>
          </div>
          <div className="stat-row">
            <span>Всего мест в перформансе:</span>
            <strong>{Object.keys(seatColors).length.toLocaleString()}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PhoneDemo;
