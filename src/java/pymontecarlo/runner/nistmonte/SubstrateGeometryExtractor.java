package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.ElectronRange;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MultiPlaneShape;

import java.io.IOException;
import java.util.Map;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Extractor for a substrate geometry.
 * 
 * @author ppinard
 */
public class SubstrateGeometryExtractor extends AbstractGeometryExtractor {

    /** XML tag. */
    private static final String TAG =
            "pymontecarlo.input.base.geometry.Substrate";



    @Override
    public void extract(Element geometryImplElement, Region chamber,
            double beamEnergy) throws IOException, EPQException {
        Map<Integer, IMaterialScatterModel> materials =
                extractMaterials(geometryImplElement);
        Map<Integer, Body> bodies =
                extractBodies(geometryImplElement, materials);

        int substrate =
                JDomUtils.getIntegerFromAttribute(geometryImplElement,
                        "substrate");
        IMaterialScatterModel material = bodies.get(substrate).material;

        double sc =
                ElectronRange.KanayaAndOkayama1972.compute(
                        material.getMaterial(), beamEnergy)
                        / material.getMaterial().getDensity();
        double dim = Math.max(10.0 * sc, 1.0e-4);
        double[] dims = new double[] { dim, dim, dim };
        double[] pos = new double[] { 0.0, 0.0, -dim / 2.0 };
        MultiPlaneShape shape = MultiPlaneShape.createBlock(dims, pos, 0, 0, 0);

        new Region(chamber, material, shape); // add shape to chamber

        extractAndApplyRotationTilt(geometryImplElement, chamber);
    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }

}
