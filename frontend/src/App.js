import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import StadiumView from './StadiumView';
import ImageUploader from './ImageUploader';
import PhoneDemo from './PhoneDemo';

function App() {
  const [seats, setSeats] = useState([]);
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState('');
  const [seatColors, setSeatColors] = useState({});
  const [loading, setLoading] = useState(false);
  const [arenaInfo, setArenaInfo] = useState(null);
  const [showPhoneDemo, setShowPhoneDemo] = useState(false);

  // Параметры генерации
  const [fillRate, setFillRate] = useState(0.8);
  const [scale, setScale] = useState(1.0);
  const [brightness, setBrightness] = useState(1.0);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Загрузить информацию об арене и местах
      const arenaRes = await axios.get('/api/preview/arena-info');
      setArenaInfo(arenaRes.data);
      setSeats(arenaRes.data.seats || []);

      // Загрузить библиотеку изображений
      const imagesRes = await axios.get('/api/images/library');
      setImages(imagesRes.data.images);
      if (imagesRes.data.images.length > 0) {
        setSelectedImage(imagesRes.data.images[0].id);
      }
    } catch (error) {
      console.error('Ошибка загрузки:', error);
    }
  };

  const handleGenerate = async () => {
    if (!selectedImage) {
      alert('Выберите изображение');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/images/generate', {
        image_id: selectedImage,
        fill_rate: fillRate,
        scale: scale,
        brightness: brightness,
        contrast: 1.0,
        rotation: 0
      });

      setSeatColors(response.data.seat_colors || {});
    } catch (error) {
      console.error('Ошибка генерации:', error);
      alert('Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleImageUploaded = (imageId) => {
    loadData();
    setSelectedImage(imageId);
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <h1>🏟️ ЦСКА Performance Generator</h1>
          <p>Каждый телефон болельщика = 1 пиксель общей картины</p>
        </div>
      </header>

      <div className="main-content">
        <div className="sidebar">
          <div className="section">
            <h2>Изображение</h2>
            <select
              value={selectedImage}
              onChange={(e) => setSelectedImage(e.target.value)}
              className="select"
            >
              {images.map(img => (
                <option key={img.id} value={img.id}>{img.name}</option>
              ))}
            </select>

            <ImageUploader onImageUploaded={handleImageUploaded} />
          </div>

          <div className="section">
            <h2>Параметры</h2>

            <div className="param">
              <label>Заполнение мест: {Math.round(fillRate * 100)}%</label>
              <input
                type="range"
                min="0.5"
                max="1"
                step="0.05"
                value={fillRate}
                onChange={(e) => setFillRate(parseFloat(e.target.value))}
              />
              <small>Процент болельщиков, участвующих в перформансе</small>
            </div>

            <div className="param">
              <label>Масштаб: {scale.toFixed(1)}x</label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={scale}
                onChange={(e) => setScale(parseFloat(e.target.value))}
              />
            </div>

            <div className="param">
              <label>Яркость: {brightness.toFixed(1)}</label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={brightness}
                onChange={(e) => setBrightness(parseFloat(e.target.value))}
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="generate-btn"
            >
              {loading ? 'Генерация...' : 'Сгенерировать перформанс'}
            </button>
          </div>

          {arenaInfo && (
            <div className="section info">
              <h3>Информация об арене</h3>
              <p>Всего мест: {arenaInfo.stats.total_seats.toLocaleString()}</p>
              <p>Размеры: {arenaInfo.dimensions[0]} × {arenaInfo.dimensions[1]} px</p>
              <p>Трибуны: {Object.keys(arenaInfo.stats.tribunes).filter(t => t !== 'null').join(', ')}</p>
            </div>
          )}
        </div>

        <div className="stadium-container">
          <div className="view-tabs">
            <button
              className={`tab-btn ${!showPhoneDemo ? 'active' : ''}`}
              onClick={() => setShowPhoneDemo(false)}
            >
              🏟️ Вид стадиона
            </button>
            <button
              className={`tab-btn ${showPhoneDemo ? 'active' : ''}`}
              onClick={() => setShowPhoneDemo(true)}
            >
              📱 Демо телефонов
            </button>
          </div>

          {!showPhoneDemo ? (
            <StadiumView
              seats={seats}
              seatColors={seatColors}
              arenaInfo={arenaInfo}
            />
          ) : (
            <PhoneDemo
              seatColors={seatColors}
              seats={seats}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
