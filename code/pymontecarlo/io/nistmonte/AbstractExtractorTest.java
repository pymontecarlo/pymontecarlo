package pymontecarlo.io.nistmonte;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.jdom.Element;
import org.jdom.Namespace;
import org.junit.Before;
import org.junit.Test;

public class AbstractExtractorTest {

    private static class ExtractorMock extends AbstractExtractor {

        public ExtractorMock(Namespace ns, String... tags) {
            super(ns, tags);
        }



        public ExtractorMock(String... tags) {
            super(tags);
        }

    }

    private Extractor extractorNoNamespace;

    private Extractor extractorWithNamespace;



    @Before
    public void setUp() throws Exception {
        extractorNoNamespace = new ExtractorMock("abc", "def");

        Namespace ns = Namespace.getNamespace("test", "http://www.example.org");
        extractorWithNamespace = new ExtractorMock(ns, "abc", "def");
    }



    @Test
    public void testCanExtractNoNamespace() {
        Namespace ns = Namespace.getNamespace("test", "http://www.example.org");

        assertTrue(extractorNoNamespace.canExtract(new Element("abc")));
        assertTrue(extractorNoNamespace.canExtract(new Element("def")));
        assertFalse(extractorNoNamespace.canExtract(new Element("hgi")));

        assertFalse(extractorNoNamespace.canExtract(new Element("abc", ns)));
        assertFalse(extractorNoNamespace.canExtract(new Element("def", ns)));
        assertFalse(extractorNoNamespace.canExtract(new Element("hgi", ns)));
    }



    @Test
    public void testCanExtractWithNamespace() {
        Namespace ns = Namespace.getNamespace("test", "http://www.example.org");

        assertTrue(extractorWithNamespace.canExtract(new Element("abc", ns)));
        assertTrue(extractorWithNamespace.canExtract(new Element("def", ns)));
        assertFalse(extractorWithNamespace.canExtract(new Element("hgi", ns)));

        assertTrue(extractorWithNamespace.canExtract(new Element("abc")));
        assertTrue(extractorWithNamespace.canExtract(new Element("def")));
        assertFalse(extractorWithNamespace.canExtract(new Element("hgi")));
    }

}
