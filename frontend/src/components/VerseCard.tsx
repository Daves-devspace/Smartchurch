import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Book } from "lucide-react";

type Verse = {
  book: string;
  chapter: number;
  verse: number;
  text: string;
};

interface VerseCardProps {
  verse: Verse;
  index: number;
}

export default function VerseCard({ verse, index }: VerseCardProps) {
  return (
    <Card className={`card-verse p-12 animate-verse-slide border-2 border-accent/20 bg-gradient-to-br from-card via-card/95 to-card/90 shadow-[var(--shadow-divine)]`} 
          style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="text-center space-y-8">
        {/* Reference Header */}
        <div className="flex items-center justify-center gap-4">
          <div className="w-16 h-16 bg-gradient-divine rounded-full flex items-center justify-center shadow-[var(--shadow-blessed)]">
            <Book className="w-8 h-8 text-primary-foreground" />
          </div>
          <div className="text-center">
            <Badge variant="secondary" className="font-sacred text-lg px-4 py-2 mb-2">
              {verse.book}
            </Badge>
            <div className="text-2xl font-sacred font-bold text-primary">
              {verse.chapter}:{verse.verse}
            </div>
          </div>
        </div>
        
        {/* Verse Text - Large and Readable for Projection */}
        <blockquote className="font-verse text-4xl md:text-5xl lg:text-6xl leading-relaxed text-foreground font-medium text-center max-w-5xl mx-auto">
          "{verse.text}"
        </blockquote>
        
        {/* Decorative Border */}
        <div className="flex items-center justify-center">
          <div className="w-32 h-1 bg-gradient-divine rounded-full opacity-60"></div>
        </div>
      </div>
    </Card>
  );
}