import itk
import os
import matplotlib.pyplot as plt
from PIL import Image


def register_multimodal(fixedImageFile: str, movingImageFile: str, exportDir=None):
    Dimension = 2
    PixelType = itk.F

    FixedImageType = itk.Image[PixelType, Dimension]
    MovingImageType = itk.Image[PixelType, Dimension]

    #  It is convenient to work with an internal image type because mutual
    #  information will perform better on images with a normalized statistical
    #  distribution. The fixed and moving images will be normalized and
    #  converted to this internal type.
    InternalPixelType = itk.F
    InternalImageType = itk.Image[InternalPixelType, Dimension]

    TransformType = itk.TranslationTransform[itk.D, Dimension]
    OptimizerType = itk.GradientDescentOptimizer
    InterpolatorType = itk.LinearInterpolateImageFunction[InternalImageType, itk.D]
    RegistrationType = itk.ImageRegistrationMethod[InternalImageType, InternalImageType]

    MetricType = itk.MutualInformationImageToImageMetric[
        InternalImageType, InternalImageType
    ]

    transform = TransformType.New()
    optimizer = OptimizerType.New()
    interpolator = InterpolatorType.New()
    registration = RegistrationType.New()
    metric = MetricType.New()

    registration.SetOptimizer(optimizer)
    registration.SetTransform(transform)
    registration.SetInterpolator(interpolator)
    registration.SetMetric(metric)

    #  The metric requires a number of parameters to be selected, including
    #  the standard deviation of the Gaussian kernel for the fixed image
    #  density estimate, the standard deviation of the kernel for the moving
    #  image density and the number of samples use to compute the densities
    #  and entropy values. Experience has
    #  shown that a kernel standard deviation of 0.4 works well for images
    #  which have been normalized to a mean of zero and unit variance.  We
    #  will follow this empirical rule in this example.
    metric.SetFixedImageStandardDeviation(0.4)
    metric.SetMovingImageStandardDeviation(0.4)

    fixedImage = itk.imread(fixedImageFile, PixelType)
    movingImage = itk.imread(movingImageFile, PixelType)

    FixedNormalizeFilterType = itk.NormalizeImageFilter[
        FixedImageType, InternalImageType
    ]

    MovingNormalizeFilterType = itk.NormalizeImageFilter[
        MovingImageType, InternalImageType
    ]

    fixedNormalizer = FixedNormalizeFilterType.New()

    movingNormalizer = MovingNormalizeFilterType.New()

    GaussianFilterType = itk.DiscreteGaussianImageFilter[
        InternalImageType, InternalImageType
    ]

    fixedSmoother = GaussianFilterType.New()
    movingSmoother = GaussianFilterType.New()

    fixedSmoother.SetVariance(2.0)
    movingSmoother.SetVariance(2.0)

    fixedNormalizer.SetInput(fixedImage)
    movingNormalizer.SetInput(movingImage)

    fixedSmoother.SetInput(fixedNormalizer.GetOutput())
    movingSmoother.SetInput(movingNormalizer.GetOutput())

    registration.SetFixedImage(fixedSmoother.GetOutput())
    registration.SetMovingImage(movingSmoother.GetOutput())

    fixedNormalizer.Update()
    fixedImageRegion = fixedNormalizer.GetOutput().GetBufferedRegion()
    registration.SetFixedImageRegion(fixedImageRegion)

    initialParameters = transform.GetParameters()

    initialParameters[0] = 0.0  # Initial offset in mm along X
    initialParameters[1] = 0.0  # Initial offset in mm along Y

    registration.SetInitialTransformParameters(initialParameters)

    #  We should now define the number of spatial samples to be considered in
    #  the metric computation. Note that we were forced to postpone this setting
    #  until we had done the preprocessing of the images because the number of
    #  samples is usually defined as a fraction of the total number of pixels in
    #  the fixed image.
    #
    #  The number of spatial samples can usually be as low as $1\%$ of the total
    #  number of pixels in the fixed image. Increasing the number of samples
    #  improves the smoothness of the metric from one iteration to another and
    #  therefore helps when this metric is used in conjunction with optimizers
    #  that rely of the continuity of the metric values. The trade-off, of
    #  course, is that a larger number of samples result in longer computation
    #  times per every evaluation of the metric.
    #
    #  It has been demonstrated empirically that the number of samples is not a
    #  critical parameter for the registration process. When you start fine
    #  tuning your own registration process, you should start high values
    #  of number of samples, for example in the range of 20% to 50% of the
    #  number of pixels in the fixed image. Once you have succeeded to register
    #  your images you can then reduce the number of samples progressively until
    #  you find a good compromise on the time it takes to compute one evaluation
    #  of the Metric. Note that it is not useful to have very fast evaluations
    #  of the Metric if the noise in their values results in more iterations
    #  being required by the optimizer to converge.
    #  behavior of the metric values as the iterations progress.
    numberOfPixels = fixedImageRegion.GetNumberOfPixels()

    numberOfSamples = int(numberOfPixels * 0.01)

    metric.SetNumberOfSpatialSamples(numberOfSamples)

    # For consistent results when regression testing.
    metric.ReinitializeSeed(121212)

    #  Since larger values of mutual information indicate better matches than
    #  smaller values, we need to maximize the cost function in this example.
    #  By default the GradientDescentOptimizer class is set to minimize the
    #  value of the cost-function. It is therefore necessary to modify its
    #  default behavior by invoking the MaximizeOn() method.
    #  Additionally, we need to define the optimizer's step size the
    #  SetLearningRate() method.
    optimizer.SetNumberOfIterations(200)
    optimizer.MaximizeOn()

    # Note that large values of the learning rate will make the optimizer
    # unstable. Small values, on the other hand, may result in the optimizer
    # needing too many iterations in order to walk to the extrema of the cost
    # function. The easy way of fine tuning this parameter is to start with
    # small values, probably in the range of {5.0, 10.0}. Once the other
    # registration parameters have been tuned for producing convergence, you
    # may want to revisit the learning rate and start increasing its value until
    # you observe that the optimization becomes unstable.  The ideal value for
    # this parameter is the one that results in a minimum number of iterations
    # while still keeping a stable path on the parametric space of the
    # optimization. Keep in mind that this parameter is a multiplicative factor
    # applied on the gradient of the Metric. Therefore, its effect on the
    # optimizer step length is proportional to the Metric values themselves.
    # Metrics with large values will require you to use smaller values for the
    # learning rate in order to maintain a similar optimizer behavior.
    optimizer.SetLearningRate(15.0)

    try:
        registration.Update()
        print(
            "Optimizer stop condition: ",
            registration.GetOptimizer().GetStopConditionDescription(),
        )
    except itk.ExceptionObject as err:
        print("case bung")

    finalParameters = registration.GetLastTransformParameters()

    TranslationAlongX = finalParameters[0]
    TranslationAlongY = finalParameters[1]

    numberOfIterations = optimizer.GetCurrentIteration()

    bestValue = optimizer.GetValue()

    # Print out results
    print("Result ")
    print(" Translation X = ", TranslationAlongX)
    print(" Translation Y = ", TranslationAlongY)
    print(" Iterations    = ", numberOfIterations)
    print(" Metric value  = ", bestValue)
    print(" Numb. Samples = ", numberOfSamples)

    ResampleFilterType = itk.ResampleImageFilter[MovingImageType, FixedImageType]

    finalTransform = TransformType.New()

    finalTransform.SetParameters(finalParameters)
    finalTransform.SetFixedParameters(transform.GetFixedParameters())

    resample = ResampleFilterType.New()

    resample.SetTransform(finalTransform)
    resample.SetInput(movingImage)
    resample.SetSize(fixedImage.GetLargestPossibleRegion().GetSize())
    resample.SetOutputOrigin(fixedImage.GetOrigin())
    resample.SetOutputSpacing(fixedImage.GetSpacing())
    resample.SetOutputDirection(fixedImage.GetDirection())
    resample.SetDefaultPixelValue(100)

    OutputPixelType = itk.UC

    OutputImageType = itk.Image[OutputPixelType, Dimension]

    CastFilterType = itk.CastImageFilter[FixedImageType, OutputImageType]

    caster = CastFilterType.New()
    caster.SetInput(resample.GetOutput())

    caster.Update()
    outputImageFile = caster.GetOutput().__array__().copy()
    # if exportDir is not None:
    #     writer = itk.ImageFileWriter[OutputImageType].New()
    #     writer.SetInput(caster.GetOutput())

    #     writer.SetFileName(outputImageFile)
    #     writer.Update()

    # Generate checkerboards before and after registration
    CheckerBoardFilterType = itk.CheckerBoardImageFilter[FixedImageType]

    checker = CheckerBoardFilterType.New()
    checker.SetInput1(fixedImage)
    checker.SetInput2(resample.GetOutput())

    caster.SetInput(checker.GetOutput())

    # Before registration
    identityTransform = TransformType.New()
    identityTransform.SetIdentity()
    resample.SetTransform(identityTransform)

    caster.Update()
    checkerBoardBefore = caster.GetOutput().__array__().copy()
    # if exportDir is not None:
    #     writer.SetFileName(checkerBoardBeforePath)
    #     writer.Update()

    # After registration
    resample.SetTransform(finalTransform)
    caster.Update()
    checkerBoardAfter = caster.GetOutput().__array__().copy()
    # if exportDir is not None:
    #     writer.SetFileName(checkerBoardAfterPath)
    #     writer.Update()

    fig, ax = plt.subplots(2, 2, figsize=(6, 6))
    ax[0][0].imshow(fixedImage, cmap="gray")
    ax[0][0].set_title("Fixed image")
    ax[0][1].imshow(movingImage, cmap="gray")
    ax[0][1].set_title("Moving image")

    ax[1][0].imshow(checkerBoardBefore, cmap="gray")
    ax[1][0].set_title("Checker board before")
    ax[1][1].imshow(checkerBoardAfter, cmap="gray")
    ax[1][1].set_title("Checker board after")

    plt.tight_layout()
    plt.show()

    if exportDir is not None:
        os.makedirs(exportDir, exist_ok=True)
        outputImageFilePath = os.path.join(exportDir, "outputImageFile.png")
        checkerBoardBeforePath = os.path.join(exportDir, "checkerBoardBefore.png")
        checkerBoardAfterPath = os.path.join(exportDir, "checkerBoardAfter.png")

        outputImageFile = Image.fromarray(outputImageFile)
        outputImageFile.save(outputImageFilePath)
        checkerBoardBefore = Image.fromarray(checkerBoardBefore)
        checkerBoardBefore.save(checkerBoardBeforePath)
        checkerBoardAfter = Image.fromarray(checkerBoardAfter)
        checkerBoardAfter.save(checkerBoardAfterPath)
