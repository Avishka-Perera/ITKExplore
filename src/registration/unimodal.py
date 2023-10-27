import itk
import matplotlib.pyplot as plt
from PIL import Image
import os


def register_unimodal(fixedImageFile, movingImageFile, exportDir=None):
    PixelType = itk.ctype("float")

    fixedImage = itk.imread(fixedImageFile, PixelType)
    movingImage = itk.imread(movingImageFile, PixelType)

    Dimension = fixedImage.GetImageDimension()
    FixedImageType = itk.Image[PixelType, Dimension]
    MovingImageType = itk.Image[PixelType, Dimension]

    TransformType = itk.TranslationTransform[itk.D, Dimension]
    initialTransform = TransformType.New()

    optimizer = itk.RegularStepGradientDescentOptimizerv4.New(
        LearningRate=4,
        MinimumStepLength=0.001,
        RelaxationFactor=0.5,
        NumberOfIterations=200,
    )

    metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()

    registration = itk.ImageRegistrationMethodv4.New(
        FixedImage=fixedImage,
        MovingImage=movingImage,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initialTransform,
    )

    movingInitialTransform = TransformType.New()
    initialParameters = movingInitialTransform.GetParameters()
    initialParameters[0] = 0
    initialParameters[1] = 0
    movingInitialTransform.SetParameters(initialParameters)
    registration.SetMovingInitialTransform(movingInitialTransform)

    identityTransform = TransformType.New()
    identityTransform.SetIdentity()
    registration.SetFixedInitialTransform(identityTransform)

    registration.SetNumberOfLevels(1)
    registration.SetSmoothingSigmasPerLevel([0])
    registration.SetShrinkFactorsPerLevel([1])

    registration.Update()

    transform = registration.GetTransform()
    finalParameters = transform.GetParameters()
    translationAlongX = finalParameters.GetElement(0)
    translationAlongY = finalParameters.GetElement(1)

    numberOfIterations = optimizer.GetCurrentIteration()

    bestValue = optimizer.GetValue()

    print("Result = ")
    print(" Translation X = " + str(translationAlongX))
    print(" Translation Y = " + str(translationAlongY))
    print(" Iterations    = " + str(numberOfIterations))
    print(" Metric value  = " + str(bestValue))

    CompositeTransformType = itk.CompositeTransform[itk.D, Dimension]
    outputCompositeTransform = CompositeTransformType.New()
    outputCompositeTransform.AddTransform(movingInitialTransform)
    outputCompositeTransform.AddTransform(registration.GetModifiableTransform())

    resampler = itk.ResampleImageFilter.New(
        Input=movingImage,
        Transform=outputCompositeTransform,
        UseReferenceImage=True,
        ReferenceImage=fixedImage,
    )
    resampler.SetDefaultPixelValue(100)

    OutputPixelType = itk.ctype("unsigned char")
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    caster = itk.CastImageFilter[FixedImageType, OutputImageType].New(Input=resampler)
    transformed_img = caster.GetOutput().__array__().copy()

    difference = itk.SubtractImageFilter.New(Input1=fixedImage, Input2=resampler)

    intensityRescaler = itk.RescaleIntensityImageFilter[
        FixedImageType, OutputImageType
    ].New(
        Input=difference,
        OutputMinimum=itk.NumericTraits[OutputPixelType].min(),
        OutputMaximum=itk.NumericTraits[OutputPixelType].max(),
    )

    resampler.SetDefaultPixelValue(1)
    difference_after = intensityRescaler.GetOutput().__array__().copy()

    resampler.SetTransform(identityTransform)
    difference_before = intensityRescaler.GetOutput().__array__().copy()

    fig, ax = plt.subplots(2, 2, figsize=(6, 6))

    ax[0][0].imshow(fixedImage, cmap="gray")
    ax[0][0].set_title("Fixed image")
    ax[0][1].imshow(movingImage, cmap="gray")
    ax[0][1].set_title("Moving image")

    ax[1][0].imshow(difference_after, cmap="gray")
    ax[1][0].set_title("Difference after")
    ax[1][1].imshow(difference_before, cmap="gray")
    ax[1][1].set_title("Difference before")

    plt.tight_layout()
    plt.show()

    if exportDir is not None:
        os.makedirs(exportDir, exist_ok=True)
        transformed_img_path = os.path.join(exportDir, "transformed_img.png")
        difference_after_path = os.path.join(exportDir, "difference_after.png")
        difference_before_path = os.path.join(exportDir, "difference_before.png")

        transformed_img = Image.fromarray(transformed_img)
        transformed_img.save(transformed_img_path)
        difference_after = Image.fromarray(difference_after)
        difference_after.save(difference_after_path)
        difference_before = Image.fromarray(difference_before)
        difference_before.save(difference_before_path)
