#include <iostream>
#include <iomanip>
#include <math.h>
#include <cstring>

class rbf
{
  public:
    rbf(int *size, int num, double *cx, double *cy, double *cz, double sigma) :
        num_(num), sigma_(sigma)
    {
      size_ = new int[3];
      for (int i = 0; i < 3; i++)
          size_[i] = size[i];

      q_ = new double[size_[0]*size_[1]*size_[2]];
  
      memset(cz_be_en_, num_, sizeof(cz_be_en_));  

      cx_ = new double[num_];
      cy_ = new double[num_];
      cz_ = new double[num_];
      for (int i = 0; i < num_; i++)
      {
        cx_[i] = cx[i];
        cy_[i] = cy[i];
        int z = cz_[i] = cz[i];

        cz_be_en_[z][1] = i;     // last index
        if (cz_be_en_[z][0] > i)
          cz_be_en_[z][0] = i;   // first index
      }

      //for (int i = 0; i < 3; i++)
      //  std::cout << cz_be_en_[i][0] << "  " << cz_be_en_[i][1] << std::endl;
    }
  

  /*
        std::cout << std::fixed << std::setprecision(3) << std::right;
        for (int i = 0; i < num_; i++)
             std::cout << std::setw(10) << cx_[i] 
                       << std::setw(10) << cy_[i] 
                       << std::setw(10) << cz_[i] << std::endl;
  */
      
    double * evaluate( double *f, double *q)
    {
      std::cout << "Internal size " << size_[0]*size_[1]*size_[2] << std::endl;

      memset(q, 0, sizeof(double)*size_[0]*size_[1]*size_[2]);

      for (int z = 0; z < size_[2]; z++)
        for (int y = 0; y < size_[1]; y++)
          for (int x = 0; x < size_[0]; x++)
            {
              int idx = x + y*size_[0] + z*size_[0]*size_[1];
              double xx = (x+0.5)/size_[0];
              double yy = (y+0.5)/size_[1];
              //std::cout << idx << " " << q[idx] << std::endl;
              for (int i = cz_be_en_[z][0]; i <= cz_be_en_[z][1]; i++)
              {
                double d = pow(xx - cx_[i], 2) + pow(yy - cy_[i], 2);
                //std::cout << xx << std::endl;
                //std::cout << xx << " " << yy << " " << cx_[i] << " " << cy_[i] << " ";
                q[idx] += exp(- d / (sigma_*sigma_));
              }
              std::cout << idx << " " << q[idx] << std::endl;
              q_[idx] = q[idx];
            }

      return q_;
    }
  
  private:
    double *q_;
    int num_;
    int *size_; 
    double *cx_, *cy_, *cz_;
    double sigma_;
    int cz_be_en_[3][2];
};


extern "C" 
{
  rbf* rbf_new(int *size, int num, double *cx, double *cy, double *cz, double sigma)
  {
    return new rbf(size, num, cx, cy, cz, sigma); 
  }
  double *rbf_evaluate(rbf* r, double *f, double *q){ return r->evaluate(f, q); }
}