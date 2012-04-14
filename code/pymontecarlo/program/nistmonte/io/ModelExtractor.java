package pymontecarlo.program.nistmonte.io;

import gov.nist.microanalysis.EPQLibrary.Strategy;

import java.io.IOException;

import org.jdom.Element;

/**
 * Extractor for the model implementations.
 * 
 * @author ppinard
 */
public interface ModelExtractor extends Extractor {

    /**
     * Extracts the model from a XML element.
     * 
     * @param modelElement
     *            XML element
     * @param strategy
     *            strategy where to set the define model
     * @throws IOException
     *             if an error occurs while reading the XML element
     */
    public void extract(Element modelElement, Strategy strategy)
            throws IOException;
}
