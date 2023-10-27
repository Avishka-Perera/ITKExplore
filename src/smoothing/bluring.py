import itk
import matplotlib.pyplot as plt
from PIL import Image
import os


def binomial(input_image_path, number_of_repetitions, output_image_path=None):
    InputPixelType = itk.F
    OutputPixelType = itk.UC
    Dimension = 2

    InputImageType = itk.Image[InputPixelType, Dimension]
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(input_image_path)

    binomialFilter = itk.BinomialBlurImageFilter.New(reader)
    binomialFilter.SetRepetitions(number_of_repetitions)

    rescaler = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
    rescaler.SetInput(binomialFilter.GetOutput())
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)

    rescaler.Update()

    out = rescaler.GetOutput().__array__()
    inp = reader.GetOutput().__array__()
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    ax[0].imshow(inp, cmap="gray")
    ax[0].set_title("Original image")
    ax[1].imshow(out, cmap="gray")
    ax[1].set_title("Processed image")
    plt.show()

    if output_image_path is not None:
        dir, _ = os.path.split(output_image_path)
        os.makedirs(dir, exist_ok=True)
        out = Image.fromarray(out)
        out.save(output_image_path)


def discrete_gaussian(input_image_path, variance, output_image_path):
    InputPixelType = itk.F
    OutputPixelType = itk.UC
    Dimension = 2

    InputImageType = itk.Image[InputPixelType, Dimension]
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(input_image_path)

    gaussianFilter = itk.DiscreteGaussianImageFilter.New(reader)
    gaussianFilter.SetVariance(variance)

    rescaler = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
    rescaler.SetInput(gaussianFilter.GetOutput())
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)

    rescaler.Update()

    out = rescaler.GetOutput().__array__()
    inp = reader.GetOutput().__array__()
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    ax[0].imshow(inp, cmap="gray")
    ax[0].set_title("Original image")
    ax[1].imshow(out, cmap="gray")
    ax[1].set_title("Processed image")
    plt.show()

    if output_image_path is not None:
        dir, _ = os.path.split(output_image_path)
        os.makedirs(dir, exist_ok=True)
        out = Image.fromarray(out)
        out.save(output_image_path)


def recursive_gaussian_iir(input_image_path, sigma, output_image_path=None):
    InputPixelType = itk.SS
    OutputPixelType = itk.UC
    Dimension = 2

    InputImageType = itk.Image[InputPixelType, Dimension]
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(input_image_path)

    filterX = itk.RecursiveGaussianImageFilter.New()
    filterX.SetDirection(0)
    filterX.SetSigma(sigma)
    filterX.SetOrder(0)
    filterX.SetNormalizeAcrossScale(False)

    filterY = itk.RecursiveGaussianImageFilter.New()
    filterY.SetDirection(1)
    filterY.SetSigma(sigma)
    filterY.SetOrder(0)
    filterY.SetNormalizeAcrossScale(False)

    filterX.SetInput(reader.GetOutput())
    filterY.SetInput(filterX.GetOutput())

    filterY.Update()

    rescaler = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
    rescaler.SetInput(filterY.GetOutput())
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)

    rescaler.Update()

    out = rescaler.GetOutput().__array__()
    inp = reader.GetOutput().__array__()
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    ax[0].imshow(inp, cmap="gray")
    ax[0].set_title("Original image")
    ax[1].imshow(out, cmap="gray")
    ax[1].set_title("Processed image")
    plt.show()

    if output_image_path is not None:
        dir, _ = os.path.split(output_image_path)
        os.makedirs(dir, exist_ok=True)
        out = Image.fromarray(out)
        out.save(output_image_path)


def median(input_image_path, radius, output_image_path=None):
    InputPixelType = itk.F
    OutputPixelType = itk.UC
    Dimension = 2

    InputImageType = itk.Image[InputPixelType, Dimension]
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(input_image_path)

    medianFilter = itk.MedianImageFilter.New(reader)
    medianFilter.SetRadius(radius)

    rescaler = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New()
    rescaler.SetInput(medianFilter.GetOutput())
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)

    rescaler.Update()

    out = rescaler.GetOutput().__array__()
    inp = reader.GetOutput().__array__()
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    ax[0].imshow(inp, cmap="gray")
    ax[0].set_title("Original image")
    ax[1].imshow(out, cmap="gray")
    ax[1].set_title("Processed image")
    plt.show()

    if output_image_path is not None:
        dir, _ = os.path.split(output_image_path)
        os.makedirs(dir, exist_ok=True)
        out = Image.fromarray(out)
        out.save(output_image_path)
