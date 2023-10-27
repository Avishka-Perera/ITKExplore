import itk
import matplotlib.pyplot as plt
import os
from PIL import Image


def grad_anisotropic_diffusion(
    inputImagePath, numberOfIterations, conductance=None, timeStep=None, exportPath=None
):
    InputPixelType = itk.F
    OutputPixelType = itk.UC
    InputImageType = itk.Image[InputPixelType, 2]
    OutputImageType = itk.Image[OutputPixelType, 2]

    FilterType = itk.GradientAnisotropicDiffusionImageFilter[
        InputImageType, InputImageType
    ]
    filter = FilterType.New()

    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(inputImagePath)
    filter.SetInput(reader.GetOutput())

    filter.SetNumberOfIterations(numberOfIterations)
    filter.SetTimeStep(timeStep)
    filter.SetConductanceParameter(conductance)
    rescaler = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
    rescaler.SetInput(filter.GetOutput())
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)

    rescaler.Update()

    input = reader.GetOutput().__array__()
    output = rescaler.GetOutput().__array__()

    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(input, cmap="gray")
    ax[0].set_title("Input image")
    ax[1].imshow(output, cmap="gray")
    ax[1].set_title("Processed image")

    plt.show()

    if exportPath is not None:
        dir, _ = os.path.split(exportPath)
        os.makedirs(dir, exist_ok=True)
        output = Image.fromarray(output)
        output.save(exportPath)


def curve_anisotropic_diffusion(
    inputImagePath,
    numberOfIterations,
    conductance=None,
    timeStep=None,
    useImageSpacing=False,
    exportPath=None,
):
    InputPixelType = itk.F
    OutputPixelType = itk.UC
    InputImageType = itk.Image[InputPixelType, 2]
    OutputImageType = itk.Image[OutputPixelType, 2]

    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(inputImagePath)

    FilterType = itk.CurvatureAnisotropicDiffusionImageFilter[
        InputImageType, InputImageType
    ]
    filter = FilterType.New()
    filter.SetInput(reader.GetOutput())

    filter.SetNumberOfIterations(numberOfIterations)
    filter.SetTimeStep(timeStep)
    filter.SetConductanceParameter(conductance)
    if useImageSpacing:
        filter.UseImageSpacingOn()

    rescaler = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
    rescaler.SetInput(filter.GetOutput())
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)

    rescaler.Update()

    input = reader.GetOutput().__array__()
    output = rescaler.GetOutput().__array__()

    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(input, cmap="gray")
    ax[0].set_title("Input image")
    ax[1].imshow(output, cmap="gray")
    ax[1].set_title("Processed image")

    plt.show()

    if exportPath is not None:
        dir, _ = os.path.split(exportPath)
        os.makedirs(dir, exist_ok=True)
        output = Image.fromarray(output)
        output.save(exportPath)
