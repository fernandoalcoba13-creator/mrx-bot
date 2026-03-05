import { config } from "../utils/config.js";

const MESSAGES = [
  "🚀 <b>¡POTENCIÁ TU TALLER 3D CON MR X!</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" +
  "Llevá tu producción al siguiente nivel con nuestras herramientas <b>¡GRATUITAS!</b> 🎁\n\n" +
  "💎 <b>SOLUCIONES PARA MAKERS:</b>\n" +
  "• 📊 <b>Calculadoras:</b> costos exactos y sistema multicolor.\n" +
  "• 🛡️ <b>Protección:</b> marca de agua para tus STL.\n" +
  "• 🤖 <b>IA:</b> diagnóstico de fallas.\n\n" +
  "⬇️ <i>Accedé desde los botones:</i>",

  "🤖 <b>¿TUS IMPRESIONES FALLAN Y NO SABÉS POR QUÉ?</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" +
  "Nuestra <b>IA de diagnóstico</b> te dice qué ajustar. ¡Gratis! 🎯\n\n" +
  "🔧 <b>TAMBIÉN:</b> costos, AMS multicolor y marca de agua.\n\n" +
  "⬇️ <i>Todo en un clic:</i>",

  "🎓 <b>¿QUERÉS DISEÑAR TUS PROPIAS PIEZAS 3D?</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" +
  "Mientras tanto, usá estas tools gratis: costos, AMS, IA y protección STL.\n\n" +
  "⬇️ <i>Hacé clic:</i>"
];

export function promoMessage(i: number) {
  return MESSAGES[i % MESSAGES.length];
}

export function promoKeyboard() {
  return {
    inline_keyboard: [
      [
        { text: "🛡️ Marcar STL", url: config.links.stlMarker },
        { text: "📊 Costos", url: config.links.costs }
      ],
      [
        { text: "🌈 AMS Multicolor", url: config.links.ams },
        { text: "🤖 IA Diagnóstico", url: config.links.ai }
      ]
    ]
  };
}
