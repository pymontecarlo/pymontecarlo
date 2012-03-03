package pymontecarlo.io.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.NISTMonte.GaussianFWHMBeam;
import gov.nist.microanalysis.NISTMonte.PencilBeam;

import java.io.IOException;

import org.jdom.Element;
import org.junit.Test;

public class BeamExtractorFactoryTest {

    public static Element createPencilBeamElement() {
        Element element =
                new Element("pencilBeam");
        element.setAttribute("energy", "1234");

        Element child = new Element("origin");
        child.setAttribute("x", "0.01");
        child.setAttribute("y", "0.02");
        child.setAttribute("z", "0.03");
        element.addContent(child);

        child = new Element("direction");
        child.setAttribute("x", "4");
        child.setAttribute("y", "5");
        child.setAttribute("z", "6");
        element.addContent(child);

        return element;
    }



    public static Element createGaussianFWHMBeamElement() {
        Element element = createPencilBeamElement();

        element.setName("gaussianBeam");
        element.setAttribute("diameter", "1e-8");

        return element;
    }



    @Test
    public void testPENCIL() throws IOException, EPQException {
        Element element = createPencilBeamElement();

        BeamExtractor extractor = BeamExtractorFactory.PENCIL;
        assertTrue(extractor.canExtract(element));

        PencilBeam beam = (PencilBeam) extractor.extract(element);
        assertEquals(1234, FromSI.eV(beam.getBeamEnergy()), 1e-4);
        assertEquals(0.01, beam.getCenter()[0], 1e-4);
        assertEquals(0.02, beam.getCenter()[1], 1e-4);
        assertEquals(0.03, beam.getCenter()[2], 1e-4);
        assertEquals(4, beam.getDirection()[0], 1e-4);
        assertEquals(5, beam.getDirection()[1], 1e-4);
        assertEquals(6, beam.getDirection()[2], 1e-4);
    }



    @Test
    public void testGAUSSIAN_FWHM() throws IOException, EPQException {
        Element element = createGaussianFWHMBeamElement();

        BeamExtractor extractor = BeamExtractorFactory.GAUSSIAN_FWHM;
        assertTrue(extractor.canExtract(element));

        GaussianFWHMBeam beam = (GaussianFWHMBeam) extractor.extract(element);
        assertEquals(1234, FromSI.eV(beam.getBeamEnergy()), 1e-4);
        assertEquals(0.01, beam.getCenter()[0], 1e-4);
        assertEquals(0.02, beam.getCenter()[1], 1e-4);
        assertEquals(0.03, beam.getCenter()[2], 1e-4);
        assertEquals(4, beam.getDirection()[0], 1e-4);
        assertEquals(5, beam.getDirection()[1], 1e-4);
        assertEquals(6, beam.getDirection()[2], 1e-4);
        assertEquals(10, beam.getDiameter() * 1e9, 1e-4);
    }
}
