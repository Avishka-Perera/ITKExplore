#include "itkGradientMagnitudeImageFilter.h"
#include "itkThresholdImageFilter.h"
#include "itkRescaleIntensityImageFilter.h"

namespace itk
{
    template <typename TImage>
    class CompositeExampleImageFilter : public ImageToImageFilter<TImage, TImage>
    {
    public:
        ITK_DISALLOW_COPY_AND_MOVE(CompositeExampleImageFilter);

        using Self = CompositeExampleImageFilter;
        using Superclass = ImageToImageFilter<TImage, TImage>;
        using Pointer = SmartPointer<Self>;
        using ConstPointer = SmartPointer<const Self>;

        using ImageType = TImage;
        using PixelType = typename ImageType::PixelType;
        itkGetMacro(Threshold, PixelType);
        itkSetMacro(Threshold, PixelType);

    protected:
        using ThresholdType = ThresholdImageFilter<ImageType>;
        using GradientType = GradientMagnitudeImageFilter<ImageType, ImageType>;
        using RescalerType = RescaleIntensityImageFilter<ImageType, ImageType>;

        typename GradientType::Pointer m_GradientFilter;
        typename ThresholdType::Pointer m_ThresholdFilter;
        typename RescalerType::Pointer m_RescaleFilter;
        PixelType m_Threshold;
    }
} // end namespace itk

template <typename TImage>
CompositeExampleImageFilter<TImage>::CompositeExampleImageFilter()
{
    m_Threshold = 1;
    m_GradientFilter = GradientType::New();
    m_ThresholdFilter = ThresholdType::New();
    m_ThresholdFilter->SetInput(m_GradientFilter->GetOutput());
    m_RescaleFilter = RescalerType::New();
    m_RescaleFilter->SetInput(m_ThresholdFilter->GetOutput());
    m_RescaleFilter->SetOutputMinimum(
        NumericTraits<PixelType>::NonpositiveMin());
    m_RescaleFilter->SetOutputMaximum(NumericTraits<PixelType>::max());
}

template <typename TImage>
void CompositeExampleImageFilter<TImage>::GenerateData()
{
    typename ImageType::Pointer input = ImageType::New();
    input->Graft(const_cast<ImageType *>(this->GetInput()));
    m_GradientFilter->SetInput(input);
    m_ThresholdFilter->ThresholdBelow(this->m_Threshold);
    m_RescaleFilter->GraftOutput(this->GetOutput());
    m_RescaleFilter->Update();
    this->GraftOutput(m_RescaleFilter->GetOutput());
}

template <typename TImage>
void CompositeExampleImageFilter<TImage>::PrintSelf(std::ostream &os, Indent indent) const
{
    Superclass::PrintSelf(os, indent);
    os << indent << "Threshold:" << this->m_Threshold << std::endl;
}