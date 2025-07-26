import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Cross, Monitor, Settings } from "lucide-react";
import { Link } from "react-router-dom";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-8">
      <Card className="w-full max-w-md bg-black/20 backdrop-blur-sm border-white/20">
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-gradient-divine rounded-full flex items-center justify-center mx-auto mb-4">
            <Cross className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-sacred text-white">
            Smartchurch Live Verses
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Link to="/live-verses">
            <Button className="w-full bg-gradient-divine hover:opacity-90">
              <Settings className="w-4 h-4 mr-2" />
              Admin Dashboard
            </Button>
          </Link>
          <Link to="/projection">
            <Button variant="outline" className="w-full bg-white/10 border-white/20 text-white hover:bg-white/20">
              <Monitor className="w-4 h-4 mr-2" />
              Projection View
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
};

export default Index;
