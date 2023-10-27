import itk


class EdgeFilter:
    InputPixelType = itk.F
    IntermediatePixelType = itk.F
    OutputPixelType = itk.UC
    Dimension = 2
    InputImageType = itk.Image[InputPixelType, Dimension]
    IntermediateImageType = itk.Image[IntermediatePixelType, Dimension]
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    def __init__(self):
        self.gradientFilter = itk.GradientMagnitudeImageFilter[
            self.InputImageType, self.IntermediateImageType
        ].New()
        self.thresholdFilter = itk.ThresholdImageFilter[
            self.IntermediateImageType
        ].New()
        self.rescaler = itk.RescaleIntensityImageFilter[
            self.IntermediateImageType, self.OutputImageType
        ].New()

        self.rescaler.SetInput(self.thresholdFilter.GetOutput())
        self.thresholdFilter.SetInput(self.gradientFilter.GetOutput())

        self.rescaler.SetOutputMinimum(0)
        self.rescaler.SetOutputMaximum(255)

    def ThresholdBelow(self, m_Threshold):
        self.thresholdFilter.ThresholdBelow(m_Threshold)

    def SetInput(self, input):
        self.gradientFilter.SetInput(input)

    def Update(self):
        self.rescaler.Update()

    def GetOutput(self):
        return self.rescaler.GetOutput()
