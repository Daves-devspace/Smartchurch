import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Play, Square, Radio, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ControlPanelProps {
  isStreaming: boolean;
  connectionStatus: "connected" | "disconnected" | "connecting";
  onStart: () => void;
  onStop: () => void;
}

export default function ControlPanel({
  isStreaming,
  connectionStatus,
  onStart,
  onStop,
}: ControlPanelProps) {
  const getStatusColor = () => {
    switch (connectionStatus) {
      case "connected":
        return "bg-green-500";
      case "connecting":
        return "bg-yellow-500";
      case "disconnected":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case "connected":
        return <Wifi className="w-4 h-4" />;
      case "connecting":
        return <Radio className="w-4 h-4 animate-pulse" />;
      case "disconnected":
        return <WifiOff className="w-4 h-4" />;
      default:
        return <WifiOff className="w-4 h-4" />;
    }
  };

  return (
    <Card className="card-divine p-6 mb-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <h2 className="font-sacred text-xl font-semibold text-primary">
              Verses Control
            </h2>
            <Badge variant="secondary" className="font-verse">
              Live Stream
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`}
            />
            <span className="text-sm font-verse text-muted-foreground capitalize">
              {connectionStatus}
            </span>
            {getStatusIcon()}
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            variant="blessed"
            size="lg"
            onClick={onStart}
            disabled={isStreaming}
            className="min-w-[120px]"
          >
            <Play className="w-4 h-4" />
            Start Stream
          </Button>

          <Button
            variant="outline"
            size="lg"
            onClick={onStop}
            disabled={!isStreaming}
            className="min-w-[120px] border-destructive/30 text-destructive hover:bg-destructive hover:text-destructive-foreground"
          >
            <Square className="w-4 h-4" />
            Stop Stream
          </Button>
        </div>
      </div>
    </Card>
  );
}
