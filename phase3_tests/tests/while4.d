//the returns aren't really tested here, they aren't even reached if the
// while/break is correctly handled. They exists as a fallback to
//avoid infinite loops if break isn't working correctly
int main() {
  while (true) {
    while (true) {
      Print(1);
      break;
      Print(2);
      return 0;
    }
    Print(3);
    break;
    Print(4);
    return 0;
  }
  Print(5);
}