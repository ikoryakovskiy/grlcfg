#include <iostream>
#include <iomanip>


class rbf
{
    public:
        rbf(int size, double *cx, double *cy, double *cz, double sigma) :
            size_(size), cx_(cx), cy_(cy), cz_(cz), sigma_(sigma)
        {
            cx_ = new double[size_];
            cy_ = new double[size_];
            cz_ = new double[size_];
            for (int i = 0; i < size_; i++)
            {
                cx_[i] = cx[i];
                cy_[i] = cy[i];
                cz_[i] = cz[i];
            } 
        }

        void evaluate()
        {
            std::cout << "Hello " << size_ << " sigma " << sigma_ << std::endl;
            std::cout << std::fixed << std::setprecision(3) << std::right;
            for (int i = 0; i < size_; i++)
                 std::cout << std::setw(10) << cx_[i] << std::setw(10) << cy_[i] << std::setw(10) << cz_[i] << std::endl;
        }

    private:
        int size_; 
        double *cx_, *cy_, *cz_;
        double sigma_;
};


extern "C" 
{
    rbf* rbf_new(int size, double *cx, double *cy, double *cz, double sigma)
    {
        return new rbf(size, cx, cy, cz, sigma); 
    }
    void  rbf_evaluate(rbf* _r){ _r->evaluate(); }
}