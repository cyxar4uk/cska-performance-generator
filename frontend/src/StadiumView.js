import React, { useRef, useEffect, useState } from 'react';
import './StadiumView.css';

const StadiumView = ({ seats, seatColors, arenaInfo }) => {
  const canvasRef = useRef(null);
  const [viewAngle, setViewAngle] = useState(0);
  const [viewHeight, setViewHeight] = useState(0.3);
  const [zoom, setZoom] = useState(1.0);
  const [showStats, setShowStats] = useState(true);
  const [selectedSector, setSelectedSector] = useState(null);
  const [hoveredSector, setHoveredSector] = useState(null);
  const [sectorStats, setSectorStats] = useState({});

  // Состояние для управления мышью
  const [isDragging, setIsDragging] = useState(false);
  const [isShiftDragging, setIsShiftDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  const [lastClickTime, setLastClickTime] = useState(0);

  // Вычислить статистику по секторам
  useEffect(() => {
    if (!seats.length) return;

    const stats = {};
    seats.forEach(seat => {
      const sector = seat.sector || 'unknown';
      if (!stats[sector]) {
        stats[sector] = {
          total: 0,
          active: 0,
          tribune: seat.tribune,
          seats: []
        };
      }
      stats[sector].total++;
      stats[sector].seats.push(seat);

      if (seatColors[String(seat.id)]) {
        stats[sector].active++;
      }
    });

    setSectorStats(stats);
  }, [seats, seatColors]);

  const handleCanvasClick = (event) => {
    // Проверка на двойной клик
    const now = Date.now();
    const isDoubleClick = now - lastClickTime < 300;
    setLastClickTime(now);

    if (isDragging) return; // Игнорировать клик после перетаскивания

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;

    // Найти ближайшее место к клику
    let closestSeat = null;
    let minDistance = Infinity;

    // Вычислить центр стадиона
    let sumX = 0, sumY = 0;
    seats.forEach(seat => {
      sumX += seat.x;
      sumY += seat.y;
    });
    const centerX = sumX / seats.length;
    const centerY = sumY / seats.length;

    seats.forEach(seat => {
      const rowNumber = seat.row || 1;
      const rowHeight = 30;
      const baseHeight = 200;
      const z = baseHeight + (rowNumber * rowHeight);

      const angleRad = (viewAngle * Math.PI) / 180;
      const pitchRad = (viewHeight * 60 - 30) * (Math.PI / 180);

      const dx = seat.x - centerX;
      const dy = seat.y - centerY;
      const rotatedX = dx * Math.cos(angleRad) - dy * Math.sin(angleRad);
      const rotatedY = dx * Math.sin(angleRad) + dy * Math.cos(angleRad);

      const cameraHeight = 300;
      const relX = rotatedX;
      const relY = rotatedY;
      const relZ = z - cameraHeight;

      const pitchedY = relY * Math.cos(pitchRad) - relZ * Math.sin(pitchRad);
      const pitchedZ = relY * Math.sin(pitchRad) + relZ * Math.cos(pitchRad);

      const fov = 800 * zoom;
      const depth = pitchedY + 1500;

      if (depth <= 100) return;

      const scale = fov / depth;
      const screenX = canvas.width / 2 + relX * scale;
      const screenY = canvas.height / 2 - pitchedZ * scale;

      const distance = Math.sqrt(
        Math.pow(screenX - clickX, 2) + Math.pow(screenY - clickY, 2)
      );

      if (distance < minDistance && distance < 50) {
        minDistance = distance;
        closestSeat = seat;
      }
    });

    if (closestSeat) {
      if (isDoubleClick) {
        // Двойной клик - фокус на сектор
        setSelectedSector(closestSeat.sector);
        // Можно добавить плавную анимацию к сектору
      } else {
        // Одиночный клик - показать информацию
        setSelectedSector(closestSeat.sector);
      }
    }
  };

  const handleMouseDown = (event) => {
    setIsDragging(true);
    setIsShiftDragging(event.shiftKey);
    setLastMousePos({ x: event.clientX, y: event.clientY });
  };

  const handleMouseMove = (event) => {
    if (!isDragging) return;

    const deltaX = event.clientX - lastMousePos.x;
    const deltaY = event.clientY - lastMousePos.y;

    if (isShiftDragging) {
      // Shift + перетаскивание = изменение высоты камеры
      const heightDelta = -deltaY * 0.001;
      setViewHeight(prev => Math.max(0, Math.min(1, prev + heightDelta)));
    } else {
      // Обычное перетаскивание = вращение
      const angleDelta = deltaX * 0.5;
      setViewAngle(prev => (prev + angleDelta) % 360);
    }

    setLastMousePos({ x: event.clientX, y: event.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setIsShiftDragging(false);
  };

  const handleWheel = (event) => {
    event.preventDefault();
    const zoomDelta = -event.deltaY * 0.001;
    setZoom(prev => Math.max(0.3, Math.min(3, prev + zoomDelta)));
  };

  // Добавить обработчики событий
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.addEventListener('wheel', handleWheel, { passive: false });
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      canvas.removeEventListener('wheel', handleWheel);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, isShiftDragging, lastMousePos, zoom, viewAngle, viewHeight]);

  useEffect(() => {
    if (!seats.length || !arenaInfo) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Очистка
    ctx.clearRect(0, 0, width, height);

    // Фон
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, '#0a0a1a');
    gradient.addColorStop(1, '#1a1a2e');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Вычислить реальный центр стадиона (среднее всех мест)
    let sumX = 0, sumY = 0;
    seats.forEach(seat => {
      sumX += seat.x;
      sumY += seat.y;
    });
    const centerX = sumX / seats.length;
    const centerY = sumY / seats.length;

    // Маркер позиции камеры (вы находитесь здесь)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Проекция 3D -> 2D с фиксированной камерой в центре
    const project = (x, y, z) => {
      const angleRad = (viewAngle * Math.PI) / 180;
      const pitchRad = (viewHeight * 60 - 30) * (Math.PI / 180); // Наклон камеры

      // Центрируем координаты относительно центра стадиона
      const dx = x - centerX;
      const dy = y - centerY;

      // Поворот вокруг вертикальной оси (камера стоит на месте, вращается вид)
      const rotatedX = dx * Math.cos(angleRad) - dy * Math.sin(angleRad);
      const rotatedY = dx * Math.sin(angleRad) + dy * Math.cos(angleRad);

      // Камера всегда в центре на фиксированной высоте
      const cameraHeight = 300; // Фиксированная высота камеры
      const relX = rotatedX;
      const relY = rotatedY;
      const relZ = z - cameraHeight;

      // Применяем наклон камеры (pitch)
      const pitchedY = relY * Math.cos(pitchRad) - relZ * Math.sin(pitchRad);
      const pitchedZ = relY * Math.sin(pitchRad) + relZ * Math.cos(pitchRad);

      // Перспективная проекция с зумом
      const fov = 800 * zoom;
      const distance = pitchedY + 1500;

      if (distance <= 100) return null;

      const scale = fov / distance;
      const screenX = width / 2 + relX * scale;
      const screenY = height / 2 - pitchedZ * scale;

      return { x: screenX, y: screenY, scale, distance };
    };

    // Проецировать и сортировать места
    const projectedSeats = [];
    seats.forEach(seat => {
      // Вычисляем высоту на основе номера ряда
      // Каждый следующий ряд поднимается выше
      const rowNumber = seat.row || 1;
      const rowHeight = 30; // высота подъема каждого ряда
      const baseHeight = 200; // базовая высота трибун
      const z = baseHeight + (rowNumber * rowHeight);

      const projected = project(seat.x, seat.y, z);

      if (projected && projected.x >= 0 && projected.x <= width &&
          projected.y >= 0 && projected.y <= height) {
        projectedSeats.push({
          ...seat,
          screenX: projected.x,
          screenY: projected.y,
          scale: projected.scale,
          distance: projected.distance,
          z: z
        });
      }
    });

    projectedSeats.sort((a, b) => b.distance - a.distance);

    // Группировка мест по секторам для отрисовки границ
    const sectorGroups = {};
    projectedSeats.forEach(seat => {
      const sector = seat.sector || 'unknown';
      if (!sectorGroups[sector]) {
        sectorGroups[sector] = [];
      }
      sectorGroups[sector].push(seat);
    });

    // Отрисовка секторов с легкой цветной подсветкой
    Object.entries(sectorGroups).forEach(([sector, seatList]) => {
      if (seatList.length === 0) return;

      // Вычислить центр сектора
      let sumX = 0, sumY = 0;
      seatList.forEach(seat => {
        sumX += seat.screenX;
        sumY += seat.screenY;
      });
      const centerSectorX = sumX / seatList.length;
      const centerSectorY = sumY / seatList.length;

      // Цвет сектора в зависимости от трибуны
      const tribune = seatList[0].tribune;
      let sectorColor;
      switch(tribune) {
        case 'A': sectorColor = 'rgba(255, 100, 100, 0.15)'; break;
        case 'B': sectorColor = 'rgba(100, 255, 100, 0.15)'; break;
        case 'C': sectorColor = 'rgba(100, 100, 255, 0.15)'; break;
        case 'D': sectorColor = 'rgba(255, 255, 100, 0.15)'; break;
        default: sectorColor = 'rgba(150, 150, 150, 0.15)';
      }

      // Подсветка сектора (легкий фон)
      const radius = Math.max(...seatList.map(s =>
        Math.sqrt(Math.pow(s.screenX - centerSectorX, 2) + Math.pow(s.screenY - centerSectorY, 2))
      ));

      if (selectedSector === sector) {
        // Выделенный сектор - ярче
        ctx.fillStyle = sectorColor.replace('0.15', '0.35');
      } else {
        ctx.fillStyle = sectorColor;
      }

      ctx.beginPath();
      ctx.arc(centerSectorX, centerSectorY, radius * 0.3, 0, Math.PI * 2);
      ctx.fill();

      // Обозначение сектора
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.font = 'bold 16px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
      ctx.lineWidth = 3;
      ctx.strokeText(sector, centerSectorX, centerSectorY);
      ctx.fillText(sector, centerSectorX, centerSectorY);
    });

    // Отрисовка мест с улучшенным освещением
    projectedSeats.forEach(seat => {
      const colorKey = String(seat.id);
      const color = seatColors[colorKey];

      // Увеличенный размер для лучшей видимости
      const baseRadius = 2.5;
      const radius = Math.max(baseRadius, seat.scale * 5);

      if (color) {
        // Добавляем затемнение для дальних рядов (эффект глубины)
        const depthFactor = Math.max(0.5, Math.min(1, seat.scale * 1.5));
        const r = Math.round(color[0] * depthFactor);
        const g = Math.round(color[1] * depthFactor);
        const b = Math.round(color[2] * depthFactor);

        // Обводка для лучшей видимости
        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.8)`;
        ctx.lineWidth = 1;
        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;

        // Добавляем свечение для активных мест
        ctx.shadowBlur = radius * 2;
        ctx.shadowColor = `rgba(${r}, ${g}, ${b}, 0.7)`;
      } else {
        // Неактивные места - более заметные серые сиденья
        ctx.fillStyle = 'rgba(200, 200, 220, 0.3)';
        ctx.strokeStyle = 'rgba(150, 150, 170, 0.5)';
        ctx.lineWidth = 0.5;
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.arc(seat.screenX, seat.screenY, radius, 0, Math.PI * 2);
      ctx.fill();
      if (color) {
        ctx.stroke();
      }

      // Сброс тени
      ctx.shadowBlur = 0;
    });

    // Информация
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = '16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Угол: ${viewAngle}°`, 20, 30);
    ctx.fillText(`Высота: ${Math.round(viewHeight * 100)}%`, 20, 55);
    ctx.fillText(`Мест отображено: ${projectedSeats.length}`, 20, 80);

  }, [seats, seatColors, viewAngle, viewHeight, arenaInfo, zoom]);

  const activeSeats = Object.keys(seatColors).length;
  const totalSeats = arenaInfo?.stats.total_seats || 0;

  return (
    <div className="stadium-view">
      <div className="view-header">
        <h2>Вид с поля на трибуны</h2>
        <button onClick={() => setShowStats(!showStats)} className="toggle-stats">
          {showStats ? 'Скрыть статистику' : 'Показать статистику'}
        </button>
      </div>

      <canvas
        ref={canvasRef}
        width={1400}
        height={800}
        className="stadium-canvas"
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      />

      <div className="controls-hint">
        <div className="hint-item">
          <span className="hint-icon">🖱️</span>
          <span>Перетащите для вращения камеры</span>
        </div>
        <div className="hint-item">
          <span className="hint-icon">🔍</span>
          <span>Колесико для зума</span>
        </div>
        <div className="hint-item">
          <span className="hint-icon">⬆️</span>
          <span>Shift + перетащите для наклона</span>
        </div>
        <div className="hint-item">
          <span className="hint-icon">👆</span>
          <span>Двойной клик на сектор</span>
        </div>
      </div>

      <div className="view-info">
        <div className="info-badge">
          <span>Угол: {Math.round(viewAngle)}°</span>
        </div>
        <div className="info-badge">
          <span>Наклон: {Math.round(viewHeight * 100)}%</span>
        </div>
        <div className="info-badge">
          <span>Зум: {zoom.toFixed(1)}x</span>
        </div>
      </div>

      <div className="preset-buttons">
        <button onClick={() => { setViewAngle(0); setViewHeight(0.5); setZoom(1); }}>
          Север
        </button>
        <button onClick={() => { setViewAngle(90); setViewHeight(0.5); setZoom(1); }}>
          Восток
        </button>
        <button onClick={() => { setViewAngle(180); setViewHeight(0.5); setZoom(1); }}>
          Юг
        </button>
        <button onClick={() => { setViewAngle(270); setViewHeight(0.5); setZoom(1); }}>
          Запад
        </button>
        <button onClick={() => { setViewAngle(45); setViewHeight(0.7); setZoom(1.2); }}>
          Обзор
        </button>
      </div>

      {showStats && activeSeats > 0 && (
        <div className="stats-overlay">
          <h3>Статистика перформанса</h3>
          <div className="stat-item">
            <span>Активных телефонов:</span>
            <strong>{activeSeats.toLocaleString()}</strong>
          </div>
          <div className="stat-item">
            <span>Всего мест:</span>
            <strong>{totalSeats.toLocaleString()}</strong>
          </div>
          <div className="stat-item">
            <span>Участие:</span>
            <strong>{Math.round((activeSeats / totalSeats) * 100)}%</strong>
          </div>
          <div className="stat-note">
            Каждая точка = телефон болельщика, светящийся определенным цветом
          </div>
        </div>
      )}


      {selectedSector && sectorStats[selectedSector] && (
        <div className="sector-info-overlay">
          <div className="sector-info-header">
            <h3>Сектор {selectedSector}</h3>
            <button
              className="close-btn"
              onClick={() => setSelectedSector(null)}
            >
              ✕
            </button>
          </div>
          <div className="sector-info-content">
            <div className="info-row">
              <span>Трибуна:</span>
              <strong>{sectorStats[selectedSector].tribune}</strong>
            </div>
            <div className="info-row">
              <span>Всего мест:</span>
              <strong>{sectorStats[selectedSector].total}</strong>
            </div>
            <div className="info-row">
              <span>Активных:</span>
              <strong className="active-count">
                {sectorStats[selectedSector].active}
              </strong>
            </div>
            <div className="info-row">
              <span>Участие:</span>
              <strong>
                {Math.round(
                  (sectorStats[selectedSector].active /
                    sectorStats[selectedSector].total) *
                    100
                )}%
              </strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StadiumView;
