int main(){
    Print("input your name:");
    Print(ReadLine());
    Print("ok bruh now input your age : ->\n", ReadInteger(), "good age? answer is ", true);

    
    if (ReadInteger()){
        Print("ok1 simple if");
    }
    
    if (ReadInteger()){
        Print("wrong");
    }else {
        Print("eyval else ham doroste");
    }
    
    if (ReadInteger()){
        if(false){
            Print("wrong");
        }else{
            Print(1);
        }
        if (true){
            Print(2);
        }     
        
        if (true){
            Print(3);
            if (false){
                Print("wrong");
            }else{
                Print(4);
                if (false){
                    Print("wrong");
                }else{
                    Print(5);
                    if (ReadInteger()){
                        Print(true);
                    }else{
                        Print(false);
                    }
                }
            }
        }else{
            Print("wrong");
        }
    }else{
        if(false){
            Print("wrong");
        }else{
            Print("wrong");
        }
        
        if (true){
            Print("wrong");
        }
    }
}
