package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MultiPlaneShape;
import gov.nist.microanalysis.Utility.Math2;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Extractor for a grain boundaries geometry.
 * 
 * @author ppinard
 */
public class GrainBoundariesGeometryExtractor extends AbstractGeometryExtractor {

    /** XML tag. */
    private static final String TAG =
            "pymontecarlo.input.base.geometry.GrainBoundaries";



    @Override
    public void extract(Element geometryImplElement, Region chamber,
            double beamEnergy) throws IOException, EPQException {
        Map<Integer, IMaterialScatterModel> materials =
                extractMaterials(geometryImplElement);
        Map<Integer, Body> bodies =
                extractBodies(geometryImplElement, materials);

        // Setup layers
        List<Layer> layers = new ArrayList<Layer>();
        double totalThickness = 0.0;

        int leftSubstrate =
                JDomUtils.getIntegerFromAttribute(geometryImplElement,
                        "left_substrate");
        layers.add(new Layer(bodies.get(leftSubstrate).material, 0.1));
        totalThickness += 0.1;

        String[] indexStrs =
                JDomUtils.getStringFromAttribute(geometryImplElement, "layers")
                        .split(",");
        Layer tmpLayer;
        for (String indexStr : indexStrs) {
            tmpLayer = (Layer) bodies.get(Integer.parseInt(indexStr));
            layers.add(tmpLayer);
            totalThickness += tmpLayer.thickness;
        }

        int rightSubstrate =
                JDomUtils.getIntegerFromAttribute(geometryImplElement,
                        "right_substrate");
        layers.add(new Layer(bodies.get(rightSubstrate).material, 0.1));
        totalThickness += 0.1;

        // Create regions
        MultiPlaneShape shape;
        double[] surfaceNormal = Math2.Z_AXIS;
        double[] layerNormal = Math2.MINUS_X_AXIS;
        double[] origin = Math2.ORIGIN_3D;
        double[] point = Math2.multiply(-totalThickness / 2.0, Math2.X_AXIS);

        IMaterialScatterModel material;
        double thickness;

        for (Layer layer : layers) {
            thickness = layer.thickness;
            material = layer.material;

            shape = MultiPlaneShape.createFilm(layerNormal, point, thickness);
            shape.addPlane(surfaceNormal, origin); // surface
            new Region(chamber, material, shape);

            // Calculate next point
            point = Math2.plus(point, Math2.multiply(thickness, Math2.X_AXIS));
        }

        extractAndApplyRotationTilt(geometryImplElement, chamber);

    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }

}
