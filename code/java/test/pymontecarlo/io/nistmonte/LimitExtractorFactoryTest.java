package pymontecarlo.io.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.EPQLibrary.EPQException;

import java.io.IOException;

import org.jdom.Element;
import org.junit.Test;

import pymontecarlo.input.nistmonte.ShowersLimit;

public class LimitExtractorFactoryTest {

    public static Element createShowersLimitElement() {
        Element element =
                new Element("pymontecarlo.input.base.limit.ShowersLimit");

        element.setAttribute("showers", "1234");

        return element;
    }



    @Test
    public void testSHOWERS() throws IOException, EPQException {
        // XML element
        Element element = createShowersLimitElement();

        // Extract
        LimitExtractor extractor = LimitExtractorFactory.SHOWERS;
        ShowersLimit limit = (ShowersLimit) extractor.extract(element);

        // Test
        assertTrue(extractor.canExtract(element));
        assertEquals(1234, limit.getMaximumShowers());
    }



    public static Element createTimeLimitElement() {
        Element element =
                new Element("pymontecarlo.input.base.limit.TimeLimit");

        element.setAttribute("time", "1234");

        return element;
    }

}
