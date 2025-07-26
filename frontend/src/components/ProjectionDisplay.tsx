import { ScrollArea } from "@/components/ui/scroll-area";
import { Cross } from "lucide-react";
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

interface ProjectionDisplayProps {
  overlays: OverlayData[];
  isFullscreen?: boolean;
}

export default function ProjectionDisplay({ overlays, isFullscreen = false }: ProjectionDisplayProps) {
  return (
    <div className={`bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden ${isFullscreen ? 'min-h-screen' : 'h-full'}`}>
      {/* Projection Background */}
      <div 
        className="absolute inset-0 opacity-10 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${churchBackground})` }}
      />
      
      {/* Main Projection Area */}
      <main className="relative z-10 flex-1 h-full flex items-center justify-center">
        {overlays.length === 0 ? (
          <div className="text-center py-20">
            <div className="space-y-8">
              <div className="w-32 h-32 bg-white/10 rounded-full flex items-center justify-center mx-auto animate-pulse">
                <Cross className="w-16 h-16 text-white/70" />
              </div>
              <div className="space-y-4">
                <h3 className="font-sacred text-4xl font-bold text-white">
                  Scripture Ready
                </h3>
                <p className="font-verse text-2xl text-white/80 max-w-2xl mx-auto">
                  Waiting for verses to display...
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="w-full max-w-7xl mx-auto p-8">
            {overlays.slice(0, 1).map((overlay, overlayIndex) => (
              <div 
                key={`overlay-${overlayIndex}`} 
                className="animate-fade-in space-y-8"
              >
                {/* Chapter Header */}
                <div className="text-center space-y-4">
                  <div className="inline-flex items-center gap-4 bg-black/30 backdrop-blur-sm rounded-full px-8 py-4 border border-white/20">
                    <div className="w-12 h-12 bg-gradient-divine rounded-full flex items-center justify-center">
                      <Cross className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="font-sacred text-3xl font-bold text-white">
                      {overlay.chunk}
                    </h2>
                  </div>
                </div>

                {/* Main Scrollable Verse Display */}
                {overlay.verses.length > 0 && (
                  <div className="space-y-6">
                    {/* Main Verse Card */}
                    <div className="bg-black/20 backdrop-blur-sm rounded-3xl p-12 border border-white/20 shadow-2xl animate-scale-in">
                      <ScrollArea className="h-[60vh] w-full">
                        <div className="text-center space-y-12">
                          {overlay.verses.map((verse, verseIndex) => (
                            <div key={`main-verse-${overlayIndex}-${verseIndex}`} className="space-y-6">
                              {/* Verse Text */}
                              <blockquote className="text-center">
                                <p className="font-verse text-4xl md:text-5xl lg:text-6xl leading-tight text-white font-medium tracking-wide">
                                  <sup className="text-2xl text-white/70 mr-2">{verse.verse}</sup>
                                  "{verse.text}"
                                </p>
                              </blockquote>
                              
                              {/* Separator between verses */}
                              {verseIndex < overlay.verses.length - 1 && (
                                <div className="flex justify-center">
                                  <div className="w-24 h-0.5 bg-white/30 rounded-full"></div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </div>
                    
                    {/* Small Reference Cards */}
                    <div className="flex flex-wrap justify-center gap-3">
                      {overlay.verses.map((verse, verseIndex) => (
                        <div
                          key={`ref-${overlayIndex}-${verseIndex}`}
                          className="bg-black/30 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20 animate-fade-in"
                          style={{ animationDelay: `${verseIndex * 0.1}s` }}
                        >
                          <span className="font-sacred text-sm font-bold text-white/90">
                            {verse.book} {verse.chapter}:{verse.verse}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Minimal Footer for Full Screen */}
      {isFullscreen && (
        <footer className="relative z-10 bg-black/20 backdrop-blur-sm border-t border-white/10">
          <div className="container mx-auto px-6 py-3">
            <div className="flex items-center justify-center">
              <p className="font-verse text-white/70 text-lg">
                "Faith comes by hearing, and hearing by the word of God" - Romans 10:17
              </p>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
}