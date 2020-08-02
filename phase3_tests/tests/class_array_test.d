class A{
    int a;
    void set_a(int a) {
        this.a = a;
    }
    int get_a(){
        return a;
    }
}

int main() {
    int i;
    A[] arr;
    arr = NewArray(10, A);
    for (i=0; i<10; i=i+1)
    {
        arr[i] = new A;
        arr[i].set_a(i);
    }
    for (i=0; i<10; i=i+1)
        Print(arr[i].get_a());

}