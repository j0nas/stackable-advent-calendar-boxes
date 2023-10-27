import adsk.core, adsk.fusion, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        features = rootComp.features
        extrudes = features.extrudeFeatures
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        tolerance = 0.5  # gap between each box for easy stacking

        initialSize = 25  # size for the largest box
        decreaseFactor = 0.5  # size decrease factor for each subsequent box
        numBoxes = 24  # number of boxes
        shellThickness = 0.4  # shell thickness

        for i in range(numBoxes):
            sketch = sketches.add(xyPlane)
            size = initialSize - (i * decreaseFactor)
            centerPoint = adsk.core.Point3D.create(i * (initialSize + tolerance), 0, 0)
            cornerPoint = adsk.core.Point3D.create(
                centerPoint.x + size, centerPoint.y + size, 0
            )
            sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                centerPoint, cornerPoint
            )

            # Get the profile defined by the rectangle
            profile = sketch.profiles.item(0)

            # Create an extrusion input
            extrudeInput = extrudes.createInput(
                profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            distance = adsk.core.ValueInput.createByReal(size)
            extrudeInput.setDistanceExtent(False, distance)

            # Create the extrusion
            extrude = extrudes.add(extrudeInput)

            # Shell the box
            shellFeatures = features.shellFeatures
            shellInputFaces = adsk.core.ObjectCollection.create()
            for face in extrude.faces:
                shellInputFaces.add(face)
            shellInput = shellFeatures.createInput(shellInputFaces, False)
            thickness = adsk.core.ValueInput.createByReal(shellThickness)
            shellInput.insideThickness = thickness
            shellFeatures.add(shellInput)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
