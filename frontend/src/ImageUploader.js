import React, { useState } from 'react';
import axios from 'axios';
import './ImageUploader.css';

const ImageUploader = ({ onImageUploaded }) => {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/api/images/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert(`Изображение "${response.data.image_id}" загружено!`);
      onImageUploaded(response.data.image_id);
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      alert('Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  return (
    <div className="image-uploader">
      <label className="upload-label">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
          className="upload-input"
        />
        <span className="upload-button">
          {uploading ? 'Загрузка...' : '📤 Загрузить своё изображение'}
        </span>
      </label>
      <small>PNG, JPG до 10MB</small>
    </div>
  );
};

export default ImageUploader;
