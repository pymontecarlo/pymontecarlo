package pymontecarlo.runner.nistmonte;

import org.jdom.Element;

/**
 * Extractor of options from a XML element.
 * 
 * @author ppinard
 */
public interface Extractor {

    /**
     * Returns whether this extract can extract options from the specified
     * element.
     * 
     * @param element
     *            XML element
     * @return <code>true</code> if this extractor can be used,
     *         <code>false</code> otherwise
     */
    public boolean canExtract(Element element);
}
