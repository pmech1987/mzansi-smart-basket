import { Capacitor } from '@capacitor/core';
import { Geolocation } from '@capacitor/geolocation';

const isNative = Capacitor.isNativePlatform();
window.MzansiNative = {
  isNative,
  getCurrentPosition(options = {}) {
    if (isNative) return Geolocation.getCurrentPosition(options);
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) return reject(new Error('Geolocation is unavailable'));
      navigator.geolocation.getCurrentPosition(resolve, reject, options);
    });
  }
};
