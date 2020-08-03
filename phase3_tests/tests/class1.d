class Binky {
   void Method() {}
}

int main() {
  Binky d;
   Binky a;
 
  d = new Binky;
  a = new Binky;
  a = d;
}