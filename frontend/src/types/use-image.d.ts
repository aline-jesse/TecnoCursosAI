// src/types/use-image.d.ts
declare module 'use-image' {
  export default function useImage(
    url: string,
    crossOrigin?: string
  ): [HTMLImageElement | undefined, string];
}
