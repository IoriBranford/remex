#!/usr/bin/python3

TileSize = 16
MiniTileSize = int(TileSize/2)
ChipsetImageWidth = TileSize*30
ChipsetImageHeight = TileSize*16
AutotileImageWidth = TileSize*3
AutotileImageHeight = TileSize*4
WaterPageWidth = TileSize*3
WaterPageHeight = TileSize*4
WaterImageWidth = WaterPageWidth*3
WaterImageHeight = WaterPageHeight*1
DecoPageWidth = TileSize*6
DecoPageHeight = TileSize*8
DecoImageWidth = DecoPageWidth*1
DecoImageHeight = DecoPageHeight*3
AutoTilesetImageWidth = TileSize*8
AutoTilesetImageHeight = TileSize*6

import xml.dom.minidom
from PIL import Image as ImagePIL
from PIL import ImageTk
from os import path
from sys import argv
from argparse import ArgumentParser
from interacter import *

class Script:
    def __init__(self, inputFileDescription, outputFileExtenion):
        self._inputFileDescription, self._outputFileExtension = inputFileDescription, outputFileExtenion

    def _printVerbose(self, message):
        if self._verbose is True:
            print(message)
            
    def _checkInputValidity(self):
        pass

    def _checkInputSize(self):
        pass
            
    def _checkArguments(self, step):
        if step == "Input exists":
            if path.exists(self._inputFilename) is False:
                print("The input {0} \"{1}\" does not exist.".format(self._inputFileDescription, self._inputFilename))
                raise SystemExit
        elif step == "Input validity":
            self._checkInputValidity()
        elif step == "Input size":
            self._checkInputSize()
        elif step == "Regions image":
            self._checkRegionsImage()
        elif step == "Output without extension":
            if self._outputFilename.lower().endswith(self._outputFileExtension) is False and self._askConfirmation is True:
                answerIgnoreNoExtension = self._interacter.askString("The output file \"{0}\" does not have a {1} extension. Shall I add the extension? (Y/n)".format(self._outputFilename, self._outputFileExtension))
                if answerIgnoreNoExtension.lower().split(" ")[0] == "y":
                    self._outputFilename += self._outputFileExtension
                    print("Ok, I'm adding the extension. The output file is now \"{0}\".".format(self._outputFilename))
                else:
                    print("Ok, I won't do anything about the extension.")
        elif step == "Output already exists":
            if path.exists(self._outputFilename) == True and self._askConfirmation is True:
                answerIgnoreExistingOutput = self._interacter.askString("The output file \"{0}\" already exists. Do you want to overwrite it? (y/N)".format(self._outputFilename))
                if answerIgnoreExistingOutput.lower().split(" ")[0] != "y":
                    print("Correct, I'm stopping here.")
                    raise SystemExit
                else:
                    print("Fine, I'll overwrite the existing file.")

    def launchScript(self, inputFilename, outputFilename, askConfirmation, verbose, testSteps=["Input exists", "Input validity", "Input size", "Output without extension", "Output already exists"]):
        self._inputFilename, self._outputFilename, self._askConfirmation, self._verbose = inputFilename.replace("\\", "/"), outputFilename.replace("\\", "/"), askConfirmation, verbose
        self._interacter = Interacter()
        i = True
        while i < len(testSteps):
            self._checkArguments(testSteps[i])
            i += 1

class TileExtractor(Script):
    def _initializeLocations(self):
        self._waterTilePositions = [
                (TileSize*0, TileSize*0),
                (TileSize*3, TileSize*0),
                (TileSize*0, TileSize*4)
                ]
        self._animTilePositions = [
                (TileSize*3, TileSize*4)
                ]
        self._autotilePositions = [
                (TileSize*0, TileSize*8),
                (TileSize*3, TileSize*8),
                (TileSize*0, TileSize*12),
                (TileSize*3, TileSize*12),
                (TileSize*6, TileSize*0),
                (TileSize*9, TileSize*0),
                (TileSize*6, TileSize*4),
                (TileSize*9, TileSize*4),
                (TileSize*6, TileSize*8),
                (TileSize*9, TileSize*8),
                (TileSize*6, TileSize*12),
                (TileSize*9, TileSize*12)
                ]
        self._lowTilePositions = [
                (TileSize*12, TileSize*0),
                (TileSize*12, TileSize*8),
                (TileSize*18, TileSize*0),
                ]
        self._highTilePositions = [
                (TileSize*18, TileSize*8),
                (TileSize*24, TileSize*0),
                (TileSize*24, TileSize*8),
                ]

    def _extractAutotiles(self, imageChipset, positions):
        autotiles = []
        for position in positions:
            autotileSurface = imageChipset.crop((position[0], position[1],
                position[0]+AutotileImageWidth, position[1]+AutotileImageHeight))
            autotiles += [autotileSurface]
        return autotiles

    def _extractDecoTiles(self, imageChipset, positions, transparentColorPos):
        image = ImagePIL.new("RGB", (DecoImageWidth, DecoImageHeight))
        i = 0
        for position in positions:
            page = imageChipset.crop((position[0], position[1],
                position[0]+DecoPageWidth, position[1]+DecoPageHeight))
            image.paste(page, (0, i*DecoPageHeight))
            i += 1

        if transparentColorPos != None:
            transparentColor = image.getpixel(transparentColorPos)
            data = image.getdata()
            alphadata = []
            for color in data:
                if color == transparentColor:
                    alphadata.append(0)
                else:
                    alphadata.append(255)

            alphaimage = ImagePIL.new("L", image.size)
            alphaimage.putdata(alphadata)
            image.putalpha(alphaimage)

        return image

    def extractTiles(self, chipsetFilename):
        imageChipset = ImagePIL.open(chipsetFilename)
        self._imageChipset = imageChipset
        self._waterTiles = self._extractAutotiles(imageChipset, self._waterTilePositions)
        self._animTiles = self._extractAutotiles(imageChipset, self._animTilePositions)
        self._autotiles = self._extractAutotiles(imageChipset, self._autotilePositions)
        self._lowTiles = self._extractDecoTiles(imageChipset, self._lowTilePositions, None)
        self._highTiles = self._extractDecoTiles(imageChipset, self._highTilePositions, (0, 0))

    def _checkInputValidity(self):
            try:
                image = ImagePIL.open(self._inputFilename)
            except IOError as error:
                print("The input chipset \"{0}\" is not a valid PNG image. Details:\n{1}".format(self._inputFilename, error))
                raise SystemExit

    def _checkInputSize(self):
            image = ImagePIL.open(self._inputFilename)
            if image.size != (ChipsetImageWidth, ChipsetImageHeight):
                print("The input chipset \"{0}\" does not have the right size.\nIt must be {1}x{2} pixels wide. Please refer to chipset formatting from RPG Maker 200x.".format(self._inputFilename, ChipsetImageWidth, ChipsetImageHeight))
                raise SystemExit

    def launchScript(self, inputFilename, outputFilename, askConfirmation, verbose, testSteps=["Input exists", "Input validity", "Input size"]):
        super().launchScript(inputFilename, outputFilename, askConfirmation, verbose, testSteps=testSteps)
        self._initializeLocations()
        self.extractTiles(self._inputFilename)
        outputFilenamePrefix = self._outputFilename
        i = 0
        for watertile in self._waterTiles:
            self._outputFilename = "{0}_w{1}{2}".format(outputFilenamePrefix, i, self._outputFileExtension)
            self._checkArguments("Output already exists")
            watertile.save(self._outputFilename, "PNG")
            self._printVerbose("Successfully created the water tile \"{0}\"!".format(self._outputFilename))
            i += 1
        i = 0
        for animtile in self._animTiles:
            self._outputFilename = "{0}_an{1}".format(outputFilenamePrefix, self._outputFileExtension)
            self._checkArguments("Output already exists")
            animtile.save(self._outputFilename, "PNG")
            self._printVerbose("Successfully created the anim tile \"{0}\"!".format(self._outputFilename))
            i += 1
        i = 0
        for autotile in self._autotiles:
            self._outputFilename = "{0}_at{1}{2}".format(outputFilenamePrefix, i, self._outputFileExtension)
            self._checkArguments("Output already exists")
            autotile.save(self._outputFilename, "PNG")
            self._printVerbose("Successfully created the autotile \"{0}\"!".format(self._outputFilename))
            i += 1

        self._outputFilename = "{0}_lo{1}".format(outputFilenamePrefix, self._outputFileExtension)
        self._checkArguments("Output already exists")
        self._lowTiles.save(self._outputFilename, "PNG")
        self._printVerbose("Successfully created the low deco tile \"{0}\"!".format(self._outputFilename))

        self._outputFilename = "{0}_hi{1}".format(outputFilenamePrefix, self._outputFileExtension)
        self._checkArguments("Output already exists")
        self._highTiles.save(self._outputFilename, "PNG")
        self._printVerbose("Successfully created the high deco tile \"{0}\"!".format(self._outputFilename))

class AutotileExpander(Script):

    def _initializeLocations(self):
        self._minitiles, self._minitilePosition, self._minitileType = dict(NO=dict(), NE=dict(), SO=dict(), SE=dict()), dict(), dict()
        self._minitileTypeDependingOnGroup, self._minitilePositionGroup = dict(), dict()
        #List of the possible types and directions
        self._minitileType, self._minitilePosition = ["Normal", "External angle", "Internal angle", "HorizontalEdge", "VerticalEdge", "Showcase", "Dummy"], ["NO", "NE", "SO", "SE"]
        #Directions depending on the position in the group
        self._minitilePositionGroup[0, 0], self._minitilePositionGroup[MiniTileSize, 0], self._minitilePositionGroup[0, MiniTileSize], self._minitilePositionGroup[MiniTileSize, MiniTileSize] = "NO", "NE", "SO", "SE"
        #Types of the minitiles depending on their groups and directions
        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*0, "NO"] = "Showcase"
        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*0, "NE"] = "Showcase"
        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*0, "SO"] = "Showcase"
        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*0, "SE"] = "Showcase"

        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*0, "NO"] = "Dummy"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*0, "NE"] = "Dummy"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*0, "SE"] = "Dummy"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*0, "SO"] = "Dummy"

        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*0, "NO"] = "External angle"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*0, "NE"] = "External angle"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*0, "SO"] = "External angle"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*0, "SE"] = "External angle"

        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*1, "NO"] = "Internal angle"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*1, "NE"] = "Internal angle"
        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*3, "SO"] = "Internal angle"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*3, "SE"] = "Internal angle"

        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*1, "NO"] = "HorizontalEdge"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*1, "NE"] = "HorizontalEdge"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*3, "SO"] = "HorizontalEdge"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*3, "SE"] = "HorizontalEdge"

        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*2, "NO"] = "VerticalEdge"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*2, "NE"] = "VerticalEdge"
        self._minitileTypeDependingOnGroup[TileSize*0, TileSize*2, "SO"] = "VerticalEdge"
        self._minitileTypeDependingOnGroup[TileSize*2, TileSize*2, "SE"] = "VerticalEdge"

        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*2, "NO"] = "Normal"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*2, "NE"] = "Normal"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*2, "SE"] = "Normal"
        self._minitileTypeDependingOnGroup[TileSize*1, TileSize*2, "SO"] = "Normal"

    def _makeAutotile(self, *types):
        autotileSurface = ImagePIL.new("RGB", (TileSize,TileSize))
        minitileAbs, minitileOrd, i = 0, 0, 0
        while minitileOrd < TileSize:
            minitileAbs = 0
            while minitileAbs < TileSize:
                minitilePosition = self._minitilePositionGroup[minitileAbs, minitileOrd]
                minitileType = types[i]
                minitileSurface = self._minitiles[minitilePosition][minitileType]
                autotileSurface.paste(minitileSurface, (minitileAbs, minitileOrd))
                i += 1
                minitileAbs += MiniTileSize
            minitileOrd += MiniTileSize
        return autotileSurface

    def expandAutotile(self, autotileFilename):
        self._imageAutotile = ImagePIL.open(autotileFilename)
        self._initializeLocations()
        #### First we find the minitiles, then we use their types and position to sort them
        groupAbs, groupOrd = 0, 0
        while groupOrd < self._imageAutotile.size[1]: #We run through the groups of minitiles
            groupAbs = 0
            while groupAbs < self._imageAutotile.size[0]:
                minitileAbs, minitileOrd = 0, 0
                while minitileOrd < TileSize: #We run through the minitiles
                    minitileAbs = 0
                    while minitileAbs < TileSize:
                        minitilePosition = self._minitilePositionGroup[minitileAbs, minitileOrd]
                        #### IB: In RPGM2k not all minitiles in the image are used
                        if (groupAbs, groupOrd, minitilePosition) in self._minitileTypeDependingOnGroup:
                            minitileType = self._minitileTypeDependingOnGroup[groupAbs, groupOrd, minitilePosition]
                            self._minitiles[minitilePosition][minitileType] = self._imageAutotile.crop((groupAbs+minitileAbs, groupOrd+minitileOrd, groupAbs+minitileAbs+MiniTileSize, groupOrd+minitileOrd+MiniTileSize))
                        minitileAbs += MiniTileSize
                    minitileOrd += MiniTileSize
                groupAbs += TileSize
            groupOrd += TileSize
        ##### We define the types composing the 48 autotiles
        autotilesSurfaces = dict()
        autotilesSurfaces[0] = self._makeAutotile("Normal", "Normal", "Normal", "Normal")
        autotilesSurfaces[1] = self._makeAutotile("External angle", "Normal", "Normal", "Normal")
        autotilesSurfaces[2] = self._makeAutotile("Normal", "External angle", "Normal", "Normal")
        autotilesSurfaces[3] = self._makeAutotile("External angle", "External angle", "Normal", "Normal")
        autotilesSurfaces[4] = self._makeAutotile("Normal", "Normal", "Normal", "External angle")
        autotilesSurfaces[5] = self._makeAutotile("External angle", "Normal", "Normal", "External angle")
        autotilesSurfaces[6] = self._makeAutotile("Normal", "External angle", "Normal", "External angle")
        autotilesSurfaces[7] = self._makeAutotile("External angle", "External angle", "Normal", "External angle")
        autotilesSurfaces[8] = self._makeAutotile("Normal", "Normal", "External angle", "Normal")
        autotilesSurfaces[9] = self._makeAutotile("External angle", "Normal", "External angle", "Normal")
        autotilesSurfaces[10] = self._makeAutotile("Normal", "External angle", "External angle", "Normal")
        autotilesSurfaces[11] = self._makeAutotile("External angle", "External angle", "External angle", "Normal")
        autotilesSurfaces[12] = self._makeAutotile("Normal", "Normal", "External angle", "External angle")
        autotilesSurfaces[13] = self._makeAutotile("External angle", "Normal", "External angle", "External angle")
        autotilesSurfaces[14] = self._makeAutotile("Normal", "External angle", "External angle", "External angle")
        autotilesSurfaces[15] = self._makeAutotile("External angle", "External angle", "External angle", "External angle")
        autotilesSurfaces[16] = self._makeAutotile("VerticalEdge", "Normal", "VerticalEdge", "Normal")
        autotilesSurfaces[17] = self._makeAutotile("VerticalEdge", "External angle", "VerticalEdge", "Normal")
        autotilesSurfaces[18] = self._makeAutotile("VerticalEdge", "Normal", "VerticalEdge", "External angle")
        autotilesSurfaces[19] = self._makeAutotile("VerticalEdge", "External angle", "VerticalEdge", "External angle")
        autotilesSurfaces[20] = self._makeAutotile("HorizontalEdge", "HorizontalEdge", "Normal", "Normal")
        autotilesSurfaces[21] = self._makeAutotile("HorizontalEdge", "HorizontalEdge", "Normal", "External angle")
        autotilesSurfaces[22] = self._makeAutotile("HorizontalEdge", "HorizontalEdge", "External angle", "Normal")
        autotilesSurfaces[23] = self._makeAutotile("HorizontalEdge", "HorizontalEdge", "External angle", "External angle")
        autotilesSurfaces[24] = self._makeAutotile("Normal", "VerticalEdge", "Normal", "VerticalEdge")
        autotilesSurfaces[25] = self._makeAutotile("Normal", "VerticalEdge", "External angle", "VerticalEdge")
        autotilesSurfaces[26] = self._makeAutotile("External angle", "VerticalEdge", "Normal", "VerticalEdge")
        autotilesSurfaces[27] = self._makeAutotile("External angle", "VerticalEdge", "External angle", "VerticalEdge")
        autotilesSurfaces[28] = self._makeAutotile("Normal", "Normal", "HorizontalEdge", "HorizontalEdge")
        autotilesSurfaces[29] = self._makeAutotile("External angle", "Normal", "HorizontalEdge", "HorizontalEdge")
        autotilesSurfaces[30] = self._makeAutotile("Normal", "External angle", "HorizontalEdge", "HorizontalEdge")
        autotilesSurfaces[31] = self._makeAutotile("External angle", "External angle", "HorizontalEdge", "HorizontalEdge")
        autotilesSurfaces[32] = self._makeAutotile("VerticalEdge", "VerticalEdge", "VerticalEdge", "VerticalEdge")
        autotilesSurfaces[33] = self._makeAutotile("HorizontalEdge", "HorizontalEdge", "HorizontalEdge", "HorizontalEdge")
        autotilesSurfaces[34] = self._makeAutotile("Internal angle", "HorizontalEdge", "VerticalEdge", "Normal")
        autotilesSurfaces[35] = self._makeAutotile("Internal angle", "HorizontalEdge", "VerticalEdge", "External angle")
        autotilesSurfaces[36] = self._makeAutotile("HorizontalEdge", "Internal angle", "Normal", "VerticalEdge")
        autotilesSurfaces[37] = self._makeAutotile("HorizontalEdge", "Internal angle", "External angle", "VerticalEdge")
        autotilesSurfaces[38] = self._makeAutotile("Normal", "VerticalEdge", "HorizontalEdge", "Internal angle")
        autotilesSurfaces[39] = self._makeAutotile("External angle", "VerticalEdge", "HorizontalEdge", "Internal angle")
        autotilesSurfaces[40] = self._makeAutotile("VerticalEdge", "Normal", "Internal angle", "HorizontalEdge")
        autotilesSurfaces[41] = self._makeAutotile("VerticalEdge", "External angle", "Internal angle", "HorizontalEdge")
        autotilesSurfaces[42] = self._makeAutotile("Showcase", "Showcase", "VerticalEdge", "VerticalEdge")
        autotilesSurfaces[43] = self._makeAutotile("Showcase", "HorizontalEdge", "Showcase", "HorizontalEdge")
        autotilesSurfaces[44] = self._makeAutotile("VerticalEdge", "VerticalEdge", "Showcase", "Showcase")
        autotilesSurfaces[45] = self._makeAutotile("HorizontalEdge", "Showcase", "HorizontalEdge", "Showcase")
        autotilesSurfaces[46] = self._makeAutotile("Showcase", "Showcase", "Showcase", "Showcase")
        autotilesSurfaces[47] = self._makeAutotile("Dummy", "Dummy", "Dummy", "Dummy")
        ##### We make the final surface by blitting our individual surfaces
        autotileAbs, autotileOrd, i, self._expandedAutotile = 0, 0, 0, ImagePIL.new("RGB", (AutoTilesetImageWidth, AutoTilesetImageHeight))
        while autotileOrd < AutoTilesetImageHeight:
            autotileAbs = 0
            while autotileAbs < AutoTilesetImageWidth:
                self._expandedAutotile.paste(autotilesSurfaces[i], (autotileAbs, autotileOrd))
                i += 1
                autotileAbs += TileSize
            autotileOrd += TileSize
        return self._expandedAutotile
            
    def _checkInputValidity(self):
            try:
                image = ImagePIL.open(self._inputFilename)
            except IOError as error:
                print("The input autotile \"{0}\" is not a valid PNG image. Details:\n{1}".format(self._inputFilename, error))
                raise SystemExit

    def _checkInputSize(self):
            image = ImagePIL.open(self._inputFilename)
            if image.size != (AutotileImageWidth, AutotileImageHeight):
                print("The input autotile \"{0}\" does not have the right size.\nIt must be {1}x{2} pixels wide. Please extract autotiles from an RPG Maker 200x chipset with this program first.".format(self._inputFilename, AutotileImageWidth, AutotileImageHeight))
                raise SystemExit

    def launchScript(self, inputFilename, outputFilename, askConfirmation, verbose, testSteps=["Input exists", "Input validity", "Input size", "Output without extension", "Output already exists"]):
        super().launchScript(inputFilename, outputFilename, askConfirmation, verbose, testSteps=testSteps)
        self.expandAutotile(self._inputFilename)
        self._expandedAutotile.save(self._outputFilename, "PNG")
        self._printVerbose("Successfully created the autotile \"{0}\"!".format(self._outputFilename))

class TilesetGenerator(Script):

    def _checkInputValidity(self):
            try:
                image = ImagePIL.open(self._inputFilename)
            except IOError as error:
                print("The input expanded autotile \"{0}\" is not a valid PNG image. Details:\n{1}".format(self._inputFilename, error))
                raise SystemExit

    def _checkInputSize(self):
            image = ImagePIL.open(self._inputFilename)
            if image.size != (AutoTilesetImageWidth, AutoTilesetImageHeight):
                print("The input expanded autotile \"{0}\" does not have the right size.\nIt must be {1}x{2} pixels wide. Please expand an autotile from RPG Maker 200x with this program first.".format(self._inputFilename, AutoTilesetImageWidth, AutoTilesetImageHeight))
                raise SystemExit

    def makeXML(self, inputFilename, outputFilename="Tileset"):
        self._inputFilename = inputFilename
        mainXML = xml.dom.minidom.getDOMImplementation().createDocument(None, "tileset", None)
        tilesetXML = mainXML.documentElement
        tilesetName = path.basename(outputFilename)
        if tilesetName.lower().endswith(".tsx") is True:
            tilesetName = tilesetName[: len(tilesetName) - 4]
        tilesetXML.setAttribute("name", tilesetName)
        tilesetXML.setAttribute("tilewidth", str(TileSize))
        tilesetXML.setAttribute("tileheight", str(TileSize))
        imageXML = mainXML.createElement("image")
        imageXML.setAttribute("source", self._inputFilename)
        imageXML.setAttribute("trans", "ffffff")
        width, height = AutoTilesetImageWidth, AutoTilesetImageHeight
        imageXML.setAttribute("width", str(width))
        imageXML.setAttribute("height", str(height))
        tilesetXML.appendChild(imageXML)
        return mainXML

    def launchScript(self, inputFilename, outputFilename, relativePath, askConfirmation, verbose, testSteps=["Input exists", "Input validity", "Input size", "Output without extension", "Output already exists"]):
        super().launchScript(inputFilename, outputFilename, askConfirmation, verbose, testSteps=testSteps)
        if relativePath is True:
            self._inputFilename = path.relpath(path.abspath(self._inputFilename), path.dirname(path.abspath(self._outputFilename))).replace("\\", "/")
        else:
            self._inputFilename = path.abspath(self._inputFilename).replace("\\", "/")
        xmlData = self.makeXML(self._inputFilename, outputFilename=outputFilename)
        with open(self._outputFilename, "w") as outputFile:
            xmlData.writexml(outputFile, addindent="  ", newl="\n", encoding="UTF-8")
        xmlData.unlink()

class RuleMaker(Script):

    def _checkInputValidity(self):
        try:
            tilesetConfig = xml.dom.minidom.parse(self._inputFilename)
            tilesetXML = tilesetConfig.documentElement
        except Exception as error:
            print("An error was encountered while loading the tileset {0}. Details:\n{1}".format(self._inputFilename,error))
            raise SystemExit

    def _checkRegionsImage(self):
        regionsOriginalLocation = path.abspath(path.dirname(argv[0])).replace("\\", "/") + "/AutomappingRegions.png"
        try:
            image = ImagePIL.open(regionsOriginalLocation)
        except IOError as error:
            print("Can't find the file \"{0}\".\nThe program should always be run within its original folder to work properly. Details:\n{1}".format(regionsOriginalLocation, error))
            raise SystemExit

    def _loadTileset(self):
        self._tilesetConfig = xml.dom.minidom.parse(self._inputFilename)
        self._tilesetXML = self._tilesetConfig.documentElement
        self._tilesetXML.setAttribute("firstgid", "1")
        self._tilesetRegionsConfig = xml.dom.minidom.getDOMImplementation().createDocument(None, "tileset", None)
        self._tilesetRegionsXML = self._tilesetRegionsConfig.documentElement
        self._tilesetRegionsXML.setAttribute("name", "Automapping Regions")
        self._tilesetRegionsXML.setAttribute("tilewidth", str(TileSize))
        self._tilesetRegionsXML.setAttribute("tileheight", str(TileSize))
        self._tilesetRegionsXML.setAttribute("firstgid", "49")
        imageTilesetRegionsXML = self._tilesetRegionsConfig.createElement("image")
        imageTilesetRegionsXML.setAttribute("width",str(TileSize))
        imageTilesetRegionsXML.setAttribute("height",str(TileSize))
        imageTilesetRegionsXML.setAttribute("trans","ffffff")
        imageTilesetRegionsXML.setAttribute("source", self._regionsLocation)
        self._tilesetRegionsXML.appendChild(imageTilesetRegionsXML)
        self._ruleConfig = xml.dom.getDOMImplementation().createDocument(None, "map", None)
        self._ruleXML = self._ruleConfig.documentElement
        self._ruleXML.setAttribute("version", "1.0")
        self._ruleXML.setAttribute("orientation", "orthogonal")
        self._ruleXML.setAttribute("width", "31")
        self._ruleXML.setAttribute("height", "23")
        self._ruleXML.setAttribute("tilewidth", str(TileSize))
        self._ruleXML.setAttribute("tileheight", str(TileSize))
        self._ruleXML.appendChild(self._tilesetXML)
        self._ruleXML.appendChild(self._tilesetRegionsXML)
    
    def _defineTilesContents(self):
        self._layerTiles, i = {"regions": dict(), "input_" + self._mapLayer: dict()}, 0
        self._layerTiles["regions"][0,8] = 0,1,1
        self._layerTiles["regions"][1,8] = 0,1,1
        self._layerTiles["regions"][2,8] = 0,1,1
        self._layerTiles["regions"][3,8] = 0,1,1
        self._layerTiles["regions"][4,8] = 0,1,0
        self._layerTiles["regions"][5,8] = 0,1,0
        self._layerTiles["regions"][6,8] = 0,1,0
        self._layerTiles["regions"][7,8] = 0,1,0
        self._layerTiles["regions"][0,9] = 1,1,1
        self._layerTiles["regions"][1,9] = 1,1,1
        self._layerTiles["regions"][2,9] = 1,1,1
        self._layerTiles["regions"][3,9] = 1,1,1
        self._layerTiles["regions"][4,9] = 1,1,1
        self._layerTiles["regions"][5,9] = 1,1,1
        self._layerTiles["regions"][6,9] = 1,1,1
        self._layerTiles["regions"][7,9] = 1,1,1
        self._layerTiles["regions"][0,10] = 0,1,1
        self._layerTiles["regions"][1,10] = 0,1,1
        self._layerTiles["regions"][2,10] = 0,1,1
        self._layerTiles["regions"][3,10] = 0,1,1
        self._layerTiles["regions"][4,10] = 1,1,1
        self._layerTiles["regions"][5,10] = 1,1,1
        self._layerTiles["regions"][6,10] = 1,1,1
        self._layerTiles["regions"][7,10] = 1,1,1
        self._layerTiles["regions"][0,12] = 1,1,0
        self._layerTiles["regions"][1,12] = 1,1,0
        self._layerTiles["regions"][2,12] = 1,1,0
        self._layerTiles["regions"][3,12] = 1,1,0
        self._layerTiles["regions"][4,12] = 1,1,1
        self._layerTiles["regions"][5,12] = 1,1,1
        self._layerTiles["regions"][6,12] = 1,1,1
        self._layerTiles["regions"][7,12] = 1,1,1
        self._layerTiles["regions"][0,13] = 1,1,1
        self._layerTiles["regions"][1,13] = 1,1,1
        self._layerTiles["regions"][2,13] = 1,1,1
        self._layerTiles["regions"][3,13] = 1,1,1
        self._layerTiles["regions"][4,13] = 1,1,1
        self._layerTiles["regions"][5,13] = 1,1,1
        self._layerTiles["regions"][6,13] = 1,1,1
        self._layerTiles["regions"][7,13] = 1,1,1
        self._layerTiles["regions"][0,14] = 1,1,0
        self._layerTiles["regions"][1,14] = 1,1,0
        self._layerTiles["regions"][2,14] = 1,1,0
        self._layerTiles["regions"][3,14] = 1,1,0
        self._layerTiles["regions"][4,14] = 0,1,0
        self._layerTiles["regions"][5,14] = 0,1,0
        self._layerTiles["regions"][6,14] = 0,1,0
        self._layerTiles["regions"][7,14] = 0,1,0
        self._layerTiles["regions"][0,16] = 0,1,0
        self._layerTiles["regions"][1,16] = 0,1,0
        self._layerTiles["regions"][2,16] = 0,1,0
        self._layerTiles["regions"][3,16] = 0,1,0
        self._layerTiles["regions"][4,16] = 0,1,0
        self._layerTiles["regions"][5,16] = 0,1,0
        self._layerTiles["regions"][6,16] = 1,1,0
        self._layerTiles["regions"][7,16] = 1,1,0
        self._layerTiles["regions"][0,17] = 1,1,1
        self._layerTiles["regions"][1,17] = 1,1,1
        self._layerTiles["regions"][2,17] = 1,1,1
        self._layerTiles["regions"][3,17] = 1,1,1
        self._layerTiles["regions"][4,17] = 1,1,1
        self._layerTiles["regions"][5,17] = 1,1,1
        self._layerTiles["regions"][6,17] = 1,1,1
        self._layerTiles["regions"][7,17] = 1,1,1
        self._layerTiles["regions"][0,18] = 0,1,0
        self._layerTiles["regions"][1,18] = 0,1,0
        self._layerTiles["regions"][2,18] = 0,1,1
        self._layerTiles["regions"][3,18] = 0,1,1
        self._layerTiles["regions"][4,18] = 1,1,0
        self._layerTiles["regions"][5,18] = 1,1,0
        self._layerTiles["regions"][6,18] = 0,1,0
        self._layerTiles["regions"][7,18] = 0,1,0
        self._layerTiles["regions"][0,20] = 0,1,1
        self._layerTiles["regions"][1,20] = 0,1,1
        self._layerTiles["regions"][2,20] = 0,1,0
        self._layerTiles["regions"][3,20] = 0,1,0
        self._layerTiles["regions"][4,20] = 0,1,0
        self._layerTiles["regions"][5,20] = 0,1,0
        self._layerTiles["regions"][6,20] = 0,1,0
        self._layerTiles["regions"][7,20] = 0,1,0
        self._layerTiles["regions"][0,21] = 1,1,1
        self._layerTiles["regions"][1,21] = 1,1,1
        self._layerTiles["regions"][2,21] = 1,1,1
        self._layerTiles["regions"][3,21] = 1,1,1
        self._layerTiles["regions"][4,21] = 1,1,1
        self._layerTiles["regions"][5,21] = 1,1,1
        self._layerTiles["regions"][6,21] = 1,1,1
        self._layerTiles["regions"][7,21] = 1,1,1
        self._layerTiles["regions"][0,22] = 0,1,0
        self._layerTiles["regions"][1,22] = 0,1,0
        self._layerTiles["regions"][2,22] = 0,1,0
        self._layerTiles["regions"][3,22] = 0,1,0
        self._layerTiles["regions"][4,22] = 0,1,0
        self._layerTiles["regions"][5,22] = 0,1,0
        self._layerTiles["regions"][6,22] = 0,1,0
        self._layerTiles["regions"][7,22] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,0] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][1,0] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][2,0] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][3,0] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,0] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,0] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][6,0] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][7,0] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][1,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][2,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][3,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][4,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][6,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][7,1] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][0,2] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][1,2] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][2,2] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][3,2] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][4,2] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][5,2] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][6,2] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][7,2] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][0,4] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][1,4] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][2,4] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][3,4] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,4] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,4] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][6,4] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][7,4] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][1,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][2,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][3,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][4,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][6,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][7,5] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][0,6] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][1,6] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][2,6] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][3,6] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][4,6] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][5,6] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][6,6] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][7,6] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,8] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][1,8] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][2,8] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][3,8] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,8] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][5,8] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][6,8] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][7,8] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][0,9] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][1,9] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][2,9] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][3,9] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][4,9] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,9] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][6,9] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][7,9] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][0,10] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][1,10] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][2,10] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][3,10] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,10] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,10] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][6,10] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][7,10] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,12] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][1,12] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][2,12] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][3,12] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,12] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,12] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][6,12] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][7,12] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,13] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][1,13] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][2,13] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][3,13] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][4,13] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][5,13] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][6,13] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][7,13] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][0,14] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][1,14] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][2,14] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][3,14] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,14] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][5,14] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][6,14] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][7,14] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][0,16] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][1,16] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][2,16] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][3,16] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][4,16] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][5,16] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][6,16] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][7,16] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,17] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][1,17] = 1,1,1
        self._layerTiles["input_" + self._mapLayer][2,17] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][3,17] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][4,17] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][5,17] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][6,17] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][7,17] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][0,18] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][1,18] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][2,18] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][3,18] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][4,18] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][5,18] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][6,18] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][7,18] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][0,20] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][1,20] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][2,20] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][3,20] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][4,20] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][5,20] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][6,20] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][7,20] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][0,21] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][1,21] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][2,21] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][3,21] = 0,1,1
        self._layerTiles["input_" + self._mapLayer][4,21] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][5,21] = 1,1,0
        self._layerTiles["input_" + self._mapLayer][6,21] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][7,21] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][0,22] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][1,22] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][2,22] = 0,1,0
        self._layerTiles["input_" + self._mapLayer][3,22] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][4,22] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][5,22] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][6,22] = 0,0,0
        self._layerTiles["input_" + self._mapLayer][7,22] = 0,0,0
        
    def _makeTile(self, tileType):
        tile = self._ruleConfig.createElement("tile")
        if tileType == "Empty":
            tile.setAttribute("gid", "0")
        elif tileType == "Regions":
            tile.setAttribute("gid", "49")
        elif isinstance(tileType, int):
            tile.setAttribute("gid", str(tileType))
        return tile

    def _getGidWithLayerAndPosition(self, layerName, x, y, groupX):
        fullOrEmptyTile = self._layerTiles[layerName][x,y][groupX]
        if fullOrEmptyTile == 1 and layerName == "regions": #On the regions layer, a full tile comes from the automapping tileset, and it's the only tile whose gid is 49
            gid = 49
        elif fullOrEmptyTile == 1 and layerName == "input_" + self._mapLayer: #On the input layers, the full tile has the value of the current tile of the autotile set (an input layer per autotile)
            gid = self._inputLayerTileCurrentGid
        elif fullOrEmptyTile == 0:
            gid = 0
        return gid

    def _makeLayerTiles(self, layerData, layerName):
        x, y, groupX, groupY, separationLineX, groupId = 0, 0, 0, 0, 0, 0
        while y < 24:
            if groupY < 3:
                x, lineX = 0, 0
                while x < 8:
                    groupX = 0
                    while groupX < 4:
                        if groupX < 3:
                            if layerName == "regions" and y < 8: #In the first part of the regions layer, we use only the regions tile
                                tile = self._makeTile("Regions")
                            elif layerName == "output_" + self._mapLayer and not (groupX == 1 and groupY == 1): #On the output layer, when we're not in the middle of the group, empty tile...
                                tile = self._makeTile("Empty")
                            elif layerName == "output_" + self._mapLayer and groupX == 1 and groupY == 1:#...But when we're in the middle, we use the value of the output tile of the group
                                tile = self._makeTile(groupId+1)
                            else: #For the rest, we use the schemes we have defined
                                tile = self._makeTile( self._getGidWithLayerAndPosition(layerName, x, y, groupX) )
                        else:
                            tile = self._makeTile("Empty")
                        layerData.appendChild(tile)
                        groupX += 1
                        lineX += 1
                    x += 1
                    if groupY == 1:
                        groupId += 1
            else:
                separationLineX = 0
                while separationLineX < 32:
                    tile = self._makeTile("Empty")
                    layerData.appendChild(tile)
                    separationLineX += 1
                groupY = -1
            y += 1
            groupY += 1

    def _convertLayerNameVersion08(self, layerName):
        if layerName == "RuleRegion":
            layerName = "regions"
        elif layerName == "RuleSet":
            layerName = "input_" + self._mapLayer
        elif layerName[:5] == "Rule_":
            layerName = "output_" + self._mapLayer
        return layerName

    def makeRule(self):
        # IB: Exclude dummy tile 48 from rules.
        # Mapper must fill layer with dummy tile before drawing,
        # to work around https://github.com/bjorn/tiled/issues/1520
        # "Sometimes, having an empty tile in the rule file makes the match fails."
        if self._version08 is False: #Tiled 0.9 style
            layers = ["regions"] +  ["input_"+self._mapLayer]*47 + ["output_"+self._mapLayer]
        else: #Tiled 0.8 style
            layers = ["RuleRegion"] + ["RuleSet"]*47 + ["Rule_"+self._mapLayer]
        i = 0
        while i < len(layers):
            layer = self._ruleConfig.createElement("layer")
            layer.setAttribute("name", layers[i])
            layer.setAttribute("width", "32")
            layer.setAttribute("height", "24")
            layerData = self._ruleConfig.createElement("data")
            layers[i] = self._convertLayerNameVersion08(layers[i]) #Once the layers have been created, we must convert the ones in 0.8 style into layers in 0.9 style, so that they work with the rest of the program
            self._makeLayerTiles(layerData, layers[i])
            layer.appendChild(layerData)
            self._ruleXML.appendChild(layer)
            if layers[i] != "regions":
                self._inputLayerTileCurrentGid += 1
            if self._inputLayerTileCurrentGid == 49:
                self._inputLayerTileCurrentGid = 1
            i += 1
        return self._ruleConfig
    
    def createRegionsImage(self, newRegionsFile=""):
        if newRegionsFile == "":
            newRegionsFile = self._regionsLocation
        try:
            automappingImage = ImagePIL.new("RGB", (TileSize, TileSize), (255, 0, 0))
            automappingImage.save(newRegionsFile, "PNG")
        except Exception as error:
            print("Can't write the regions image to the location \"{0}\".\nMake sure that the location isn't read-only, or try to launch the program in admin/root mode. Details:\n{1}".format(self._regionsLocation, error))
            raise SystemExit

    def setRegionsLocation(self, regionsLocation):
        if regionsLocation == "": #No regions location: we use the folder of the output file
            self._regionsLocation =  path.abspath(path.dirname(self._outputFilename)).replace("\\", "/") + "/automappingRegions.png"
        else: 
            self._regionsLocation = path.abspath(regionsLocation).replace("\\", "/") + "/automappingRegions.png"

    def initializeEverything(self, inputFilename="", mapLayer="", version08=""):
        if inputFilename != "":
            self._inputFilename = inputFilename.replace("\\", "/")
        if mapLayer != "":
            self._mapLayer = mapLayer
        if version08 != "":
            self._version08 = version08
        self._loadTileset()
        self._defineTilesContents()
        self._inputLayerTileCurrentGid = 1

    def unlinkOtherData(self):
        self._ruleConfig.unlink()
        self._tilesetConfig.unlink()
        self._tilesetRegionsConfig.unlink()

    def launchScript(self, inputFilename, outputFilename, mapLayer, regionsLocation, version08, askConfirmation, verbose, testSteps=["Input exists", "Input validity", "Regions image", "Output without extension", "Output already exists"]):
        super().launchScript(inputFilename, outputFilename, askConfirmation, verbose, testSteps=testSteps)
        originalRegionsFile, self._mapLayer, self._version08 = path.abspath(path.dirname(argv[0])).replace("\\", "/") + "/automappingRegions.png", mapLayer, version08
        self.setRegionsLocation(regionsLocation)
        self.createRegionsImage()
        self.initializeEverything()
        xmlData = self.makeRule()
        with open(self._outputFilename, "w") as outputFile:
            xmlData.writexml(outputFile, addindent="  ", newl="\n", encoding="UTF-8")
        xmlData.unlink()
        self.unlinkOtherData()

if __name__ == "__main__":
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", description="The command to execute", dest="command")
    extractSubCommand = subparsers.add_parser("extract", help="Tile Extractor. Extracts the water tiles, animated tiles, autotiles, low tiles, and high tiles from an RPG Maker 200x chipset into individual images.")
    extractSubCommand.add_argument("-o", "--output", metavar="outputPrefix", dest="outputPrefix", default="extractedTiles", help="The prefix for each output file. By default, it is \"extractedTiles\", so the output files will be \"extractedTiles_at[0..11].png\", \"extractedTiles_w[0..2].png\", \"extractedTiles_an.png\", \"extractedTiles_lo.png\", and \"extractedTiles_hi.png\", located in the directory in which you launch the script. The script will ask you whether it should overwrite each file that already exists, unless you used the force option.")
    extractSubCommand.add_argument("inputChipset", help="The chipset from which to extract. It must follow a few rules. It must be a PNG image, {0}x{1} wide. It must use RPG Maker 200x's chipset formatting.".format(ChipsetImageWidth, ChipsetImageHeight))
    extractSubCommand.add_argument("-f", "--force", action="store_false", dest="askConfirmation", help="Forces the script to be executed without asking you anything. The script will overwrite every output file without warning you if it already exists.")
    extractSubCommand.add_argument("-v", "--verbose", action="store_true", help="Starts the program in verbose mode: it prints detailed information on the process.")
    expandSubCommand = subparsers.add_parser("expand", help="Autotile Expander. Expands an autotile from RPG Maker 200x into a grid containing all the possible cases.")
    expandSubCommand.add_argument("-o", "--output", metavar="outputAutotile", dest="outputAutotile", default="expandedAutotile.png", help="The output file (the expanded autotile). By default, it is \"expandedAutotile.png\", located in the directory in which you launch the script. The script will ask you whether it should overwrite the file if it already exists, unless you used the force option.")
    expandSubCommand.add_argument("inputAutotile", help="The autotile to expand. It must follow a few rules. It must be a PNG image, {0}x{1} wide. It must use RPG Maker 200x's Autotile formatting.".format(AutotileImageWidth, AutotileImageHeight))
    expandSubCommand.add_argument("-f", "--force", action="store_false", dest="askConfirmation", help="Forces the script to be executed without asking you anything. The script will overwrite the output file without warning you if it already exists. Furthermore, it won't ask add an extension to the output file if it lacks.")
    expandSubCommand.add_argument("-v", "--verbose", action="store_true", help="Starts the program in verbose mode: it prints detailed information on the process.")
    makeTilesetSubCommand = subparsers.add_parser("maketileset", help="Tileset Generator. Generates a tileset for Tiled map editor with an expanded autotile. You can use it directly (but manually) in your maps, or use it with the Rule Maker to make an automatic automapping rule.")
    makeTilesetSubCommand.add_argument("-o", "--output", metavar="outputTileset", dest="outputTileset", default="expandedAutotileTileset.tsx", help="The output file (the tileset). By default, it is \"expandedAutotileTileset.tsx\", located in the directory in which you launch the script. The script will ask you whether it should overwrite the file if it already exists, unless you used the force option.")
    makeTilesetSubCommand.add_argument("inputExpandedAutotile", help="The expanded autotile to make a tileset with. It must be a PNG image, {0}x{1} wide. To get this expanded autotile, use the autotile expander featured with Remex (with the command \"expand\").".format(AutoTilesetImageWidth, AutoTilesetImageHeight))
    makeTilesetSubCommand.add_argument("-f", "--force", action="store_false", dest="askConfirmation", help="Forces the script to be executed without asking you anything. The script will overwrite the output file without warning you if it already exists. Furthermore, it won't ask add an extension to the output file if it lacks.")
    makeTilesetSubCommand.add_argument("-r", "--relative", action="store_true", dest="relativePath", help="In the tileset file, use a relative path to the image itself. Warning: the same relative path will be used in the rulemap if you generate one with this tileset. To avoid any problem regarding paths, you should put your tilesets, maps and images in the same folder.")
    makeTilesetSubCommand.add_argument("-v", "--verbose", action="store_true", help="Starts the program in verbose mode: it prints detailed information on the process.")
    makeRuleSubCommand = subparsers.add_parser("makerule", help="Rule Maker. Generates an automapping rule for Tiled map editor using a tileset of an expanded autotile. It enables you to map autotiles automatically, without worrying about the precise case to use.")
    makeRuleSubCommand.add_argument("inputTileset", help="The tileset for Tiled to make an automapping rule with. It must be a tsx file referring to an expanded autotile. To get the expanded autotile, use the autotile expander featured with Remex (with the command \"expand\"). To get the tileset, use the tileset maker featured with Remex (with the command \"maketileset\").")
    makeRuleSubCommand.add_argument("-o", "--output", metavar="outputRule", dest="outputRule", default="automappingRule.tmx", help="The output file (the automapping rule). By default, it is \"automappingrule.tmx\", located in the directory in which you launch the script. The script will ask you whether it should overwrite the file if it already exists, unless you used the force option.")
    makeRuleSubCommand.add_argument("-l", "--layer", metavar="mapLayer", dest="mapLayer", default="Tile Layer 1", help="The name of the map layer to consider during the automapping. By default, it is \"Tile Layer 1\". You can only choose a layer per rule, so you need to make another rule if you want another layer to be considered too.")
    makeRuleSubCommand.add_argument("-r", "--regions", metavar="regionsLocation", dest="regionsLocation", default="", help="The rulemap requires an additional image to work properly. By default, the image is always created in the folder of the rulemap. But if you want to, you can set another location.")
    makeRuleSubCommand.add_argument("-8", "--v08", dest="version08", action="store_true", help="Formats the rulemap for the 0.8 version of Tiled. By default, the rulemaker formats the rule for the 0.9 version.")
    makeRuleSubCommand.add_argument("-f", "--force", action="store_false", dest="askConfirmation", help="Forces the script to be executed without asking you anything. The script will overwrite the output file without warning you if it already exists. Furthermore, it won't ask add an extension to the output file if it lacks.")
    makeRuleSubCommand.add_argument("-v", "--verbose", action="store_true", help="Starts the program in verbose mode: it prints detailed information on the process.")
    answers = vars(parser.parse_args())
    command, verbose, askConfirmation = answers["command"], answers["verbose"], answers["askConfirmation"]
    if command == "extract":
        tileExtractor, outputPrefix, inputChipset = TileExtractor("chipset", ".png"), answers["outputPrefix"], answers["inputChipset"]
        tileExtractor.launchScript(inputChipset, outputPrefix, askConfirmation, verbose)
    elif command == "expand":
        autotileExpander, outputAutotile, inputAutotile = AutotileExpander("autotile", ".png"), answers["outputAutotile"], answers["inputAutotile"]
        autotileExpander.launchScript(inputAutotile, outputAutotile, askConfirmation, verbose)
    elif command == "maketileset":
        tilesetGenerator, outputTileset, inputExpandedAutotile = TilesetGenerator("expanded autotile", ".tsx"), answers["outputTileset"], answers["inputExpandedAutotile"]
        relativePath = answers["relativePath"]
        tilesetGenerator.launchScript(inputExpandedAutotile, outputTileset, relativePath, askConfirmation, verbose)
    elif command == "makerule":
        ruleMaker, outputRule, inputTileset, mapLayer = RuleMaker("automapping rule", ".tmx"), answers["outputRule"], answers["inputTileset"], answers["mapLayer"]
        regionsLocation, version08 = answers["regionsLocation"], answers["version08"]
        ruleMaker.launchScript(inputTileset, outputRule, mapLayer, regionsLocation, version08, askConfirmation, verbose)
