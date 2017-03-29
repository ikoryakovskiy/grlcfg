#include <iostream>

int size; 
double *cx, *cy, *cz;

class Repc{
    public:
        void evaluate()
        {
            std::cout << "Hello " << size << std::endl;
        }
};


extern "C" {
    Repc* repc_new(int _size, double *_cx, double *_cy, double *_cz)
    {
        size = _size;
        cx = _cx; cy = _cy; cz = _cz;
        return new Repc(); 
    }
    void  repc_evaluate(Repc* _r){ _r->evaluate(); }
}