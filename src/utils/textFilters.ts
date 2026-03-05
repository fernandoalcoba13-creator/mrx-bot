const urlRegex = /(https?:\/\/\S+|t\.me\/\S+|www\.\S+)/i;

const bannedScripts = [
  /[\u4E00-\u9FFF]/, // CJK
  /[\u0600-\u06FF]/, // Arabic
  /[\u0400-\u04FF]/, // Cyrillic
  /[\uAC00-\uD7AF]/  // Hangul
];

export function hasExternalLink(text: string): boolean {
  return urlRegex.test(text);
}

export function hasBannedLanguage(text: string): boolean {
  return bannedScripts.some(r => r.test(text));
}
