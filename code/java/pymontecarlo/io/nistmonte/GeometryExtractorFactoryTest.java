package pymontecarlo.io.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.Material;
import gov.nist.microanalysis.EPQLibrary.MaterialFactory;
import gov.nist.microanalysis.EPQLibrary.ToSI;
import gov.nist.microanalysis.NISTMonte.BasicMaterialModel;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.RegionBase;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Shape;

import java.io.IOException;

import org.jdom.Element;
import org.junit.Before;
import org.junit.Test;

public class GeometryExtractorFactoryTest {

    private Region chamber;

    private double beamEnergy;



    protected static Element createMaterialsElement() throws EPQException {
        Element element = new Element("materials");

        Material mat = MaterialFactory.createCompound("Si3N4", 3.44);
        IMaterialScatterModel model = new BasicMaterialModel(mat);
        model.setMinEforTracking(ToSI.eV(1234));
        element.addContent(createMaterialElement(model, 1));

        mat = MaterialFactory.createCompound("Al2O3", 4.53);
        model = new BasicMaterialModel(mat);
        model.setMinEforTracking(ToSI.eV(4321));
        element.addContent(createMaterialElement(model, 2));

        mat =
                MaterialFactory
                        .createPureElement(gov.nist.microanalysis.EPQLibrary.Element.Au);
        model = new BasicMaterialModel(mat);
        model.setMinEforTracking(ToSI.eV(50));
        element.addContent(createMaterialElement(model, 3));

        return element;
    }



    private static Element createMaterialElement(IMaterialScatterModel model,
            int index) {
        Material mat = model.getMaterial();

        Element element =
                new Element("pymontecarlo.input.base.material.Material");
        element.setAttribute("index", Integer.toString(index));
        element.setAttribute("name", mat.getName());
        element.setAttribute("density", Double.toString(mat.getDensity()));
        element.setAttribute("absorptionEnergyElectron",
                Double.toString(FromSI.eV(model.getMinEforTracking())));

        Element compositionElement = new Element("composition");
        Element elementElement;
        for (gov.nist.microanalysis.EPQLibrary.Element el : mat.getElementSet()) {
            elementElement = new Element("element");

            elementElement.setAttribute("z",
                    Integer.toString(el.getAtomicNumber()));
            elementElement.setAttribute("weightFraction",
                    Double.toString(mat.weightFraction(el, false)));

            compositionElement.addContent(elementElement);
        }
        element.addContent(compositionElement);

        return element;
    }



    private static Element createBodyElement(int index, int materialIndex) {
        Element element = new Element("pymontecarlo.input.base.body.Body");

        element.setAttribute("index", Integer.toString(index));
        element.setAttribute("material", Integer.toString(materialIndex));

        return element;
    }



    private static Element createLayerElement(int index, int materialIndex,
            double thickness) {
        Element element = new Element("pymontecarlo.input.base.body.Layer");

        element.setAttribute("index", Integer.toString(index));
        element.setAttribute("material", Integer.toString(materialIndex));
        element.setAttribute("thickness", Double.toString(thickness));

        return element;
    }



    public static Element createSubstrateGeometryElement() throws EPQException {
        Element element =
                new Element("pymontecarlo.input.base.geometry.Substrate");
        element.setAttribute("substrate", "0");
        element.setAttribute("rotation", "0.0");
        element.setAttribute("tilt", Double.toString(Math.toRadians(30.0)));

        element.addContent(createMaterialsElement());

        Element bodiesElement = new Element("bodies");
        bodiesElement.addContent(createBodyElement(0, 1));
        element.addContent(bodiesElement);

        return element;
    }



    @Before
    public void setUp() throws Exception {
        chamber = new Region(null, null, null);
        beamEnergy = ToSI.eV(15e3);
    }



    @Test
    public void testSUBSTRATE() throws IOException, EPQException {
        // Setup
        Element element = createSubstrateGeometryElement();

        // Extract
        GeometryExtractor extractor = GeometryExtractorFactory.SUBSTRATE;
        double[] n = extractor.extract(element, chamber, beamEnergy);

        // Test
        assertTrue(extractor.canExtract(element));

        assertEquals(0.866025404, n[0], 1e-4);
        assertEquals(0.0, n[1], 1e-4);
        assertEquals(0.5, n[2], 1e-4);
        assertEquals(Math.toRadians(30.0), Math.atan2(n[2], n[0]), 1e-4);

        assertEquals(1, chamber.getSubRegions().size());
        RegionBase region = chamber.getSubRegions().get(0);

        IMaterialScatterModel model = region.getScatterModel();
        assertEquals(1234, FromSI.eV(model.getMinEforTracking()), 1e-4);

        Material mat = region.getMaterial();
        assertEquals("Si3N4", mat.getName());
        assertEquals(3.44, mat.getDensity(), 1e-2);
        assertEquals(2, mat.getElementSet().size());
    }



    public static Element createMultiLayersGeometryElement()
            throws EPQException {
        Element element =
                new Element("pymontecarlo.input.base.geometry.MultiLayers");
        element.setAttribute("substrate", "2");
        element.setAttribute("layers", "0,1");
        element.setAttribute("tilt", Double.toString(Math.toRadians(30.0)));
        element.setAttribute("rotation", Double.toString(Math.toRadians(180)));

        element.addContent(createMaterialsElement());

        Element bodiesElement = new Element("bodies");
        bodiesElement.addContent(createBodyElement(2, 3));
        bodiesElement.addContent(createLayerElement(0, 1, 50e-9));
        bodiesElement.addContent(createLayerElement(1, 2, 150e-9));
        element.addContent(bodiesElement);

        return element;
    }



    @Test
    public void testMULTI_LAYERS() throws IOException, EPQException {
        // Setup
        Element element = createMultiLayersGeometryElement();

        // Extract
        GeometryExtractor extractor = GeometryExtractorFactory.MULTI_LAYERS;
        double[] n = extractor.extract(element, chamber, beamEnergy);

        // Tests
        assertTrue(extractor.canExtract(element));

        assertEquals(-0.866025404, n[0], 1e-4);
        assertEquals(0.0, n[1], 1e-4);
        assertEquals(0.5, n[2], 1e-4);
        assertEquals(Math.toRadians(30.0), Math.atan2(n[2], -n[0]), 1e-4);

        assertEquals(3, chamber.getSubRegions().size());

        // Test layer 1
        RegionBase region = chamber.getSubRegions().get(0);

        IMaterialScatterModel model = region.getScatterModel();
        assertEquals(1234, FromSI.eV(model.getMinEforTracking()), 1e-4);

        Material mat = region.getMaterial();
        assertEquals("Si3N4", mat.getName());
        assertEquals(3.44, mat.getDensity(), 1e-2);
        assertEquals(2, mat.getElementSet().size());

        Shape shape = region.getShape();
        assertFalse(shape.contains(new double[] { 0.0, 0.0, 0.01 })); // above
        assertTrue(shape.contains(new double[] { 0.0, 0.0, -25e-9 })); // in
        assertFalse(shape.contains(new double[] { 0.0, 0.0, -0.01 })); // below

        // Test layer 2
        region = chamber.getSubRegions().get(1);

        model = region.getScatterModel();
        assertEquals(4321, FromSI.eV(model.getMinEforTracking()), 1e-4);

        mat = region.getMaterial();
        assertEquals("Al2O3", mat.getName());
        assertEquals(4.53, mat.getDensity(), 1e-2);
        assertEquals(2, mat.getElementSet().size());

        shape = region.getShape();
        assertFalse(shape.contains(new double[] { 0.0, 0.0, -25e-9 })); // above
        assertTrue(shape.contains(new double[] { 0.0, 0.0, -125e-9 })); // in
        assertFalse(shape.contains(new double[] { 0.0, 0.0, -0.01 })); // below

        // Test substrate
        region = chamber.getSubRegions().get(2);

        model = region.getScatterModel();
        assertEquals(50.0, FromSI.eV(model.getMinEforTracking()), 1e-4);

        mat = region.getMaterial();
        assertEquals("Pure gold", mat.getName());
        assertEquals(19300, mat.getDensity(), 1e-2);
        assertEquals(1, mat.getElementSet().size());
    }



    public static Element createGrainBoundariesGeometryElement()
            throws EPQException {
        Element element =
                new Element("pymontecarlo.input.base.geometry.GrainBoundaries");
        element.setAttribute("left_substrate", "0");
        element.setAttribute("right_substrate", "2");
        element.setAttribute("layers", "1");
        element.setAttribute("rotation", "0.0");
        element.setAttribute("tilt", Double.toString(Math.toRadians(30.0)));

        element.addContent(createMaterialsElement());

        Element bodiesElement = new Element("bodies");
        bodiesElement.addContent(createBodyElement(2, 3));
        bodiesElement.addContent(createBodyElement(0, 1));
        bodiesElement.addContent(createLayerElement(1, 2, 150e-9));
        element.addContent(bodiesElement);

        return element;
    }



    @Test
    public void testGRAIN_BOUNDARIES() throws IOException, EPQException {
        // Setup
        Element element = createGrainBoundariesGeometryElement();

        // Extract
        GeometryExtractor extractor = GeometryExtractorFactory.GRAIN_BOUNDARIES;
        double[] n = extractor.extract(element, chamber, beamEnergy);

        // Test
        assertTrue(extractor.canExtract(element));

        assertEquals(0.866025404, n[0], 1e-4);
        assertEquals(0.0, n[1], 1e-4);
        assertEquals(0.5, n[2], 1e-4);
        assertEquals(Math.toRadians(30.0), Math.atan2(n[2], n[0]), 1e-4);

        assertEquals(3, chamber.getSubRegions().size());

        // Test left substrate
        RegionBase region = chamber.getSubRegions().get(0);

        IMaterialScatterModel model = region.getScatterModel();
        assertEquals(1234, FromSI.eV(model.getMinEforTracking()), 1e-4);

        Material mat = region.getMaterial();
        assertEquals("Si3N4", mat.getName());
        assertEquals(3.44, mat.getDensity(), 1e-2);
        assertEquals(2, mat.getElementSet().size());

        Shape shape = region.getShape();
        assertFalse(shape.contains(new double[] { 0.0, 0.0, 0.01 })); // above
        assertTrue(shape.contains(new double[] { -80e-9, 0.0, -50e-8 })); // in
        assertFalse(shape.contains(new double[] { 0.0, 0.0, -50e-8 })); // right

        // Test layer
        region = chamber.getSubRegions().get(1);

        model = region.getScatterModel();
        assertEquals(4321, FromSI.eV(model.getMinEforTracking()), 1e-4);

        mat = region.getMaterial();
        assertEquals("Al2O3", mat.getName());
        assertEquals(4.53, mat.getDensity(), 1e-2);
        assertEquals(2, mat.getElementSet().size());

        shape = region.getShape();
        assertFalse(shape.contains(new double[] { 0.0, 0.0, 0.01 })); // above
        assertFalse(shape.contains(new double[] { -80e-9, 0.0, -50e-8 })); // left
        assertTrue(shape.contains(new double[] { 0.0, 0.0, -50e-8 })); // in
        assertFalse(shape.contains(new double[] { 80e-9, 0.0, -50e-8 })); // right

        // Test right substrate
        region = chamber.getSubRegions().get(2);

        model = region.getScatterModel();
        assertEquals(50.0, FromSI.eV(model.getMinEforTracking()), 1e-4);

        mat = region.getMaterial();
        assertEquals("Pure gold", mat.getName());
        assertEquals(19300, mat.getDensity(), 1e-2);
        assertEquals(1, mat.getElementSet().size());

        shape = region.getShape();
        assertFalse(shape.contains(new double[] { 0.0, 0.0, 0.01 })); // above
        assertTrue(shape.contains(new double[] { 80e-9, 0.0, -50e-8 })); // in
        assertFalse(shape.contains(new double[] { 0.0, 0.0, -50e-8 })); // left
    }
}
