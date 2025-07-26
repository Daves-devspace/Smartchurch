import { Card } from "@/components/ui/card";
import { Mic, Clock } from "lucide-react";

interface ChunkDisplayProps {
  chunk: string;
  timestamp?: string;
}

export default function ChunkDisplay({ chunk, timestamp }: ChunkDisplayProps) {
  return (
    <Card className="card-divine p-6 mb-6 border-l-4 border-accent">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center animate-holy-glow">
            <Mic className="w-5 h-5 text-primary-foreground" />
          </div>
        </div>
        
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="font-sacred text-sm font-semibold text-primary">
              Live Transcription
            </h3>
            {timestamp && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span>{timestamp}</span>
              </div>
            )}
          </div>
          
          <p className="font-verse text-base leading-relaxed text-foreground bg-secondary/50 rounded-lg p-4">
            {chunk}
          </p>
        </div>
      </div>
    </Card>
  );
}