//
// Classes with inheritance
//

class Animal {
  int height;
  Animal mother;
  void InitAnimal(int h, Animal mom) {
    this.height = h;
    mother = mom;
  }

  int GetHeight() {
    return height;
  }

  Animal GetMom() {
    return this.mother;
  }
}

class Cow extends Animal {
  bool isSpotted;
  void InitCow(int h, Animal m) {
    isSpotted = true;
    this.InitAnimal(h, m);
  }
  bool IsSpottedCow () {
    return isSpotted;
  }
}


void main() {
  Cow betsy;
  Animal b;
  betsy = new Cow;

  betsy.InitCow(5, null);
  b = betsy;
  b.GetMom();
  Print("spots: ",betsy.IsSpottedCow(), "    height: ", b.GetHeight());
}
