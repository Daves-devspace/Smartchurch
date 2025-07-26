import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import ControlPanel from "@/components/ControlPanel";
import ProjectionDisplay from "@/components/ProjectionDisplay";
import {
  Cross,
  Monitor,
  Eye,
  Book,
  Settings,
  Activity,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
} from "lucide-react";
import churchBackground from "@/assets/church-background.jpg";

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

interface AdminDashboardProps {
  overlays: OverlayData[];
  isStreaming: boolean;
  connectionStatus: "connected" | "disconnected" | "connecting";
  onStart: () => void;
  onStop: () => void;
}

// Sample related verses for demonstration
const relatedVerses = [
  {
    book: "John",
    chapter: 1,
    verse: 1,
    text: "In the beginning was the Word, and the Word was with God, and the Word was God.",
  },
  {
    book: "Colossians",
    chapter: 1,
    verse: 16,
    text: "For by him were all things created, that are in heaven, and that are in earth, visible and invisible.",
  },
  {
    book: "Hebrews",
    chapter: 11,
    verse: 3,
    text: "Through faith we understand that the worlds were framed by the word of God.",
  },
  {
    book: "Psalm",
    chapter: 33,
    verse: 6,
    text: "By the word of the LORD were the heavens made; and all the host of them by the breath of his mouth.",
  },
];

export default function AdminDashboard({
  overlays,
  isStreaming,
  connectionStatus,
  onStart,
  onStop,
}: AdminDashboardProps) {
  const [textPosition, setTextPosition] = useState<"bottom" | "middle" | "top">(
    "bottom"
  );
  const [overlayTiming, setOverlayTiming] = useState<"5" | "10" | "manual">(
    "5"
  );
  const [isManualControl, setIsManualControl] = useState(false);
  const [selectedVerseIndex, setSelectedVerseIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  const openProjectionView = () => {
    window.open("/projection", "_blank");
  };

  // Flatten all verses from all overlays for navigation
  const allVerses = overlays.flatMap((overlay) => overlay.verses);

  // Determine which verse to show
  const currentVerse =
    isManualControl && allVerses.length > 0
      ? allVerses[selectedVerseIndex]
      : overlays[0]?.verses[0];

  // Navigation functions
  const goToPreviousVerse = () => {
    if (allVerses.length > 0) {
      setSelectedVerseIndex((prev) =>
        prev > 0 ? prev - 1 : allVerses.length - 1
      );
      setIsManualControl(true);
    }
  };

  const goToNextVerse = () => {
    if (allVerses.length > 0) {
      setSelectedVerseIndex((prev) =>
        prev < allVerses.length - 1 ? prev + 1 : 0
      );
      setIsManualControl(true);
    }
  };

  const selectVerse = (verseIndex: number) => {
    setSelectedVerseIndex(verseIndex);
    setIsManualControl(true);
    setIsPaused(true);
  };

  const resumeAutoMode = () => {
    setIsManualControl(false);
    setIsPaused(false);
    setSelectedVerseIndex(0);
  };

  const togglePause = () => {
    setIsPaused(!isPaused);
    if (!isPaused) {
      setIsManualControl(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="font-sacred text-2xl font-bold text-white">
              VerseOverlay System
            </h1>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-white text-sm">OBS Connected</span>
              </div>
              <Button
                onClick={openProjectionView}
                size="sm"
                className="bg-gradient-divine hover:opacity-90"
              >
                <Monitor className="w-4 h-4 mr-2" />
                Projection
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <div className="flex flex-col xl:flex-row gap-6 h-[calc(100vh-140px)]">
          {/* Left Sidebar - Live Verse Detection */}
          <div className="w-full xl:w-80 flex-shrink-0">
            <Card className="bg-black/20 backdrop-blur-sm border-white/20 h-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-lg flex items-center gap-2">
                  <Activity className="w-5 h-5 text-green-500" />
                  Live Detection
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0 h-[calc(100%-80px)]">
                <ScrollArea className="h-full pr-2">
                  <div className="space-y-3">
                    {overlays.length === 0 ? (
                      <div className="text-center py-8">
                        <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-3">
                          <Eye className="w-6 h-6 text-white/50" />
                        </div>
                        <p className="text-white/70 text-sm">
                          Listening for verses...
                        </p>
                      </div>
                    ) : (
                      allVerses.map((verse, index) => (
                        <div
                          key={`verse-${index}`}
                          onClick={() => selectVerse(index)}
                          className={`bg-white/5 rounded-lg p-3 border transition-all duration-200 cursor-pointer group ${
                            isManualControl && selectedVerseIndex === index
                              ? "border-blue-500/60 bg-blue-500/10"
                              : "border-white/10 hover:bg-white/10"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <div
                                className={`w-2 h-2 rounded-full ${
                                  isManualControl &&
                                  selectedVerseIndex === index
                                    ? "bg-blue-500"
                                    : "bg-green-500 animate-pulse"
                                }`}
                              ></div>
                              <span className="text-white/50 text-xs">
                                {new Date().toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              {isManualControl &&
                                selectedVerseIndex === index && (
                                  <Badge
                                    variant="secondary"
                                    className="text-xs bg-blue-500/20 text-blue-300 border-blue-500/30"
                                  >
                                    Selected
                                  </Badge>
                                )}
                              {!isManualControl && index === 0 && (
                                <Badge
                                  variant="secondary"
                                  className="text-xs bg-white/10 text-white/80"
                                >
                                  Live
                                </Badge>
                              )}
                            </div>
                          </div>
                          <div
                            className={`font-semibold text-sm transition-colors ${
                              isManualControl && selectedVerseIndex === index
                                ? "text-blue-300"
                                : "text-white group-hover:text-blue-300"
                            }`}
                          >
                            {verse.book} {verse.chapter}:{verse.verse}
                          </div>
                          <div className="text-white/70 text-xs line-clamp-2 mt-1">
                            {verse.text}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Main Content - Livestream Preview */}
          <div className="flex-1 min-h-0">
            <Card className="bg-black/20 backdrop-blur-sm border-white/20 h-full">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-lg flex items-center gap-2">
                  <Monitor className="w-5 h-5 text-blue-500" />
                  Livestream Preview
                  {isStreaming && (
                    <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-1"></div>
                      LIVE
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0 h-[calc(100%-80px)]">
                <div className="relative w-full h-full rounded-xl overflow-hidden shadow-2xl">
                  {/* Bible Background Image */}
                  <div
                    className="absolute inset-0 bg-cover bg-center transition-all duration-500"
                    style={{
                      backgroundImage: `url(${churchBackground})`,
                      filter: "brightness(0.6) contrast(1.1)",
                    }}
                  />

                  {/* Gradient Overlay for Better Text Contrast */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />

                  {/* Verse Overlay */}
                  {currentVerse && (
                    <div
                      className={`absolute left-0 right-0 px-8 py-8 transition-all duration-500 ${
                        textPosition === "bottom"
                          ? "bottom-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent"
                          : textPosition === "middle"
                          ? "top-1/2 -translate-y-1/2 bg-black/80 backdrop-blur-md"
                          : "top-0 bg-gradient-to-b from-black/90 via-black/70 to-transparent"
                      }`}
                    >
                      <div className="text-center space-y-4 max-w-4xl mx-auto">
                        <div className="flex items-center justify-center gap-3 mb-2">
                          <div className="w-8 h-0.5 bg-gradient-to-r from-transparent to-gold-400"></div>
                          <Book className="w-5 h-5 text-gold-400" />
                          <div className="w-8 h-0.5 bg-gradient-to-l from-transparent to-gold-400"></div>
                        </div>
                        <h3 className="text-gold-400 font-bold text-2xl lg:text-3xl tracking-wide">
                          {currentVerse.book} {currentVerse.chapter}:
                          {currentVerse.verse}
                        </h3>
                        <p className="text-white text-lg lg:text-xl font-verse leading-relaxed max-w-3xl mx-auto drop-shadow-lg">
                          "{currentVerse.text}"
                        </p>
                      </div>
                    </div>
                  )}

                  {/* No verse state */}
                  {!currentVerse && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center space-y-6">
                        <div className="relative">
                          <Cross className="w-20 h-20 text-white/30 mx-auto" />
                          <div className="absolute inset-0 w-20 h-20 border-2 border-white/20 rounded-full animate-pulse mx-auto"></div>
                        </div>
                        <div className="space-y-2">
                          <p className="text-white/80 text-xl font-semibold">
                            Waiting for verse detection...
                          </p>
                          <p className="text-white/60 text-sm">
                            Speak or reference a Bible verse to see it displayed
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar - Settings & Controls */}
          <div className="w-full xl:w-80 flex-shrink-0 space-y-4">
            {/* Control Panel */}
            <Card className="bg-black/20 backdrop-blur-sm border-white/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-lg flex items-center gap-2">
                  <Settings className="w-5 h-5 text-purple-500" />
                  Controls
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="space-y-4">
                  {/* Verse Navigation Controls */}
                  <div className="bg-white/5 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-white font-semibold text-sm">
                        Verse Control
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-white/60">
                          {allVerses.length > 0
                            ? `${selectedVerseIndex + 1}/${allVerses.length}`
                            : "0/0"}
                        </span>
                        <div
                          className={`w-2 h-2 rounded-full ${
                            isManualControl
                              ? "bg-blue-500"
                              : "bg-green-500 animate-pulse"
                          }`}
                        ></div>
                        <span
                          className={`text-xs ${
                            isManualControl ? "text-blue-400" : "text-green-400"
                          }`}
                        >
                          {isManualControl ? "Manual" : "Auto"}
                        </span>
                      </div>
                    </div>

                    <div className="flex gap-1 mb-3">
                      <Button
                        onClick={goToPreviousVerse}
                        disabled={allVerses.length === 0}
                        size="sm"
                        variant="outline"
                        className="flex-1 bg-black/30 border-white/20 text-white hover:bg-white/10 disabled:opacity-50"
                      >
                        <SkipBack className="w-3 h-3 mr-1" />
                        Prev
                      </Button>

                      <Button
                        onClick={togglePause}
                        disabled={allVerses.length === 0}
                        size="sm"
                        variant="outline"
                        className="bg-black/30 border-white/20 text-white hover:bg-white/10 disabled:opacity-50"
                      >
                        {isPaused ? (
                          <Play className="w-3 h-3" />
                        ) : (
                          <Pause className="w-3 h-3" />
                        )}
                      </Button>

                      <Button
                        onClick={goToNextVerse}
                        disabled={allVerses.length === 0}
                        size="sm"
                        variant="outline"
                        className="flex-1 bg-black/30 border-white/20 text-white hover:bg-white/10 disabled:opacity-50"
                      >
                        Next
                        <SkipForward className="w-3 h-3 ml-1" />
                      </Button>
                    </div>

                    <Button
                      onClick={resumeAutoMode}
                      disabled={!isManualControl}
                      size="sm"
                      className="w-full bg-green-600/80 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-xs"
                    >
                      <RotateCcw className="w-3 h-3 mr-1" />
                      Resume Auto Mode
                    </Button>
                  </div>

                  {/* Verses Control Section */}
                  <div className="bg-white/5 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-white font-semibold text-sm">
                        Verses Control
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-white/60">
                          Live Stream
                        </span>
                        <div
                          className={`w-2 h-2 rounded-full ${
                            isStreaming
                              ? "bg-green-500 animate-pulse"
                              : "bg-red-500"
                          }`}
                        ></div>
                        <span
                          className={`text-xs ${
                            isStreaming ? "text-green-400" : "text-red-400"
                          }`}
                        >
                          {isStreaming ? "Connected" : "Disconnected"}
                        </span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        onClick={onStart}
                        disabled={isStreaming}
                        className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm py-2"
                      >
                        Start Stream
                      </Button>
                      <Button
                        onClick={onStop}
                        disabled={!isStreaming}
                        variant="destructive"
                        className="flex-1 disabled:opacity-50 disabled:cursor-not-allowed text-sm py-2"
                      >
                        Stop Stream
                      </Button>
                    </div>
                  </div>

                  {/* Connection Status */}
                  <div className="bg-white/5 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-white/70 text-sm">
                        Connection Status
                      </span>
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            connectionStatus === "connected"
                              ? "bg-green-500"
                              : connectionStatus === "connecting"
                              ? "bg-yellow-500 animate-pulse"
                              : "bg-red-500"
                          }`}
                        ></div>
                        <span
                          className={`text-sm capitalize ${
                            connectionStatus === "connected"
                              ? "text-green-400"
                              : connectionStatus === "connecting"
                              ? "text-yellow-400"
                              : "text-red-400"
                          }`}
                        >
                          {connectionStatus}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Overlay Settings */}
            <Card className="bg-black/20 backdrop-blur-sm border-white/20 flex-1">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-lg">
                  Display Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0 space-y-6">
                {/* Font Settings */}
                <div className="space-y-3">
                  <label className="text-white font-semibold text-sm">
                    Font Style
                  </label>
                  <select className="w-full bg-black/30 border border-white/20 rounded-lg px-3 py-2 text-white text-sm focus:border-white/40 focus:ring-1 focus:ring-white/20 transition-colors">
                    <option value="modern">Modern Sans</option>
                    <option value="classic">Classic Serif</option>
                    <option value="serif">Traditional</option>
                  </select>
                </div>

                {/* Text Position */}
                <div className="space-y-3">
                  <label className="text-white font-semibold text-sm">
                    Text Position
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(["top", "middle", "bottom"] as const).map((position) => (
                      <label key={position} className="relative cursor-pointer">
                        <input
                          type="radio"
                          name="textPosition"
                          value={position}
                          checked={textPosition === position}
                          onChange={(e) =>
                            setTextPosition(
                              e.target.value as typeof textPosition
                            )
                          }
                          className="sr-only"
                        />
                        <div
                          className={`p-3 rounded-lg border text-center text-xs font-medium transition-all ${
                            textPosition === position
                              ? "bg-blue-500/20 border-blue-500/50 text-blue-300"
                              : "bg-black/20 border-white/20 text-white/70 hover:border-white/30"
                          }`}
                        >
                          {position.charAt(0).toUpperCase() + position.slice(1)}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Overlay Timing */}
                <div className="space-y-3">
                  <label className="text-white font-semibold text-sm">
                    Auto-Hide Timer
                  </label>
                  <div className="space-y-2">
                    {(["5", "10", "manual"] as const).map((timing) => (
                      <label
                        key={timing}
                        className="flex items-center gap-3 cursor-pointer group"
                      >
                        <div className="relative">
                          <input
                            type="radio"
                            name="overlayTiming"
                            value={timing}
                            checked={overlayTiming === timing}
                            onChange={(e) =>
                              setOverlayTiming(
                                e.target.value as typeof overlayTiming
                              )
                            }
                            className="sr-only"
                          />
                          <div
                            className={`w-4 h-4 rounded-full border-2 transition-all ${
                              overlayTiming === timing
                                ? "border-blue-500 bg-blue-500"
                                : "border-white/30 group-hover:border-white/50"
                            }`}
                          >
                            {overlayTiming === timing && (
                              <div className="w-2 h-2 bg-white rounded-full absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
                            )}
                          </div>
                        </div>
                        <span className="text-white text-sm group-hover:text-white/90">
                          {timing === "manual"
                            ? "Manual control"
                            : `${timing} seconds`}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Status Indicator */}
                <div className="pt-4 border-t border-white/20">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/70">System Status</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-green-400">Active</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
