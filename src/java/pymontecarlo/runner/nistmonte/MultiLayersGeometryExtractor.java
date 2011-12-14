package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.ElectronRange;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MultiPlaneShape;
import gov.nist.microanalysis.Utility.Math2;

import java.io.IOException;
import java.util.Map;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Extractor for a multi-layers geometry.
 * 
 * @author ppinard
 */
public class MultiLayersGeometryExtractor extends AbstractGeometryExtractor {

    /** XML tag. */
    private static final String TAG =
            "pymontecarlo.input.base.geometry.MultiLayers";



    @Override
    public void extract(Element geometryImplElement, Region chamber,
            double beamEnergy) throws IOException, EPQException {
        Map<Integer, IMaterialScatterModel> materials =
                extractMaterials(geometryImplElement);
        Map<Integer, Body> bodies =
                extractBodies(geometryImplElement, materials);

        // Layers
        String[] tmpLayers =
                JDomUtils.getStringFromAttribute(geometryImplElement, "layers")
                        .split(",");

        MultiPlaneShape shape;
        double[] normal = Math2.Z_AXIS;
        double[] point = Math2.ORIGIN_3D;

        Layer layer;
        IMaterialScatterModel material;
        double thickness;
        for (String tmpLayer : tmpLayers) {
            layer = (Layer) bodies.get(Integer.parseInt(tmpLayer));
            thickness = layer.thickness;
            material = layer.material;

            shape = MultiPlaneShape.createFilm(normal, point, thickness);
            new Region(chamber, material, shape); // add shape to chamber

            // Calculate next point
            point = Math2.minus(point, Math2.multiply(thickness, Math2.Z_AXIS));
        }

        int substrate =
                JDomUtils.getIntegerFromAttribute(geometryImplElement,
                        "substrate", -1);
        if (substrate > 0) {
            material = bodies.get(substrate).material;

            double sc =
                    ElectronRange.KanayaAndOkayama1972.compute(
                            material.getMaterial(), beamEnergy)
                            / material.getMaterial().getDensity();
            double dim = Math.max(10.0 * sc, 1.0e-4);
            double[] dims = new double[] { dim, dim, dim };
            point = Math2.minus(point, Math2.multiply(dim / 2.0, Math2.Z_AXIS));
            shape = MultiPlaneShape.createBlock(dims, point, 0, 0, 0);

            new Region(chamber, material, shape); // add shape to chamber
        }

        extractAndApplyRotationTilt(geometryImplElement, chamber);

    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }

}
