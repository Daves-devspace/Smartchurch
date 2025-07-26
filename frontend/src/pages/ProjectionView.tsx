import { useEffect, useState, useRef } from "react";
import ProjectionDisplay from "@/components/ProjectionDisplay";

type Verse = {
  book: string;
  chapter: number;
  verse: number;
  text: string;
};

type OverlayData = {
  chunk: string;
  verses: Verse[];
  timestamp?: string;
};

export default function ProjectionView() {
  const [overlays, setOverlays] = useState<OverlayData[]>([
    {
      chunk: "Genesis Chapter 1: The Creation",
      verses: [
        {
          book: "Genesis",
          chapter: 1,
          verse: 1,
          text: "In the beginning God created the heaven and the earth."
        },
        {
          book: "Genesis", 
          chapter: 1,
          verse: 2,
          text: "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters."
        },
        {
          book: "Genesis",
          chapter: 1,
          verse: 3,
          text: "And God said, Let there be light: and there was light."
        },
        {
          book: "Genesis",
          chapter: 1,
          verse: 4,
          text: "And God saw the light, that it was good: and God divided the light from the darkness."
        },
        {
          book: "Genesis",
          chapter: 1,
          verse: 5,
          text: "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day."
        }
      ],
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const dataWs = useRef<WebSocket | null>(null);

  // Data socket for incoming overlay data
  useEffect(() => {
    function setUpDataSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/verses/`);
      dataWs.current = ws;

      ws.onopen = () => {
        console.log("Projection WS connected");
      };
      
      ws.onmessage = (e) => {
        const data: OverlayData = JSON.parse(e.data);
        const timestamp = new Date().toLocaleTimeString();
        setOverlays((prev) => [{ ...data, timestamp }, ...prev].slice(0, 10));
      };
      
      ws.onclose = () => {
        console.log("Projection WS disconnected, retrying in 3s");
        setTimeout(setUpDataSocket, 3000);
      };
    }

    setUpDataSocket();

    return () => {
      dataWs.current?.close();
    };
  }, []);

  return <ProjectionDisplay overlays={overlays} isFullscreen={true} />;
}