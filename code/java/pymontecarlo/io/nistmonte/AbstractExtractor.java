package pymontecarlo.io.nistmonte;

import org.jdom.Element;

/**
 * Abstract implementation of the extractor interface.
 * 
 * @author ppinard
 */
public abstract class AbstractExtractor implements Extractor {

    /** XML tag. */
    private final String tag;



    /**
     * Creates a new <code>AbstractExtractor</code>.
     * 
     * @param tag
     *            required XML tag
     */
    public AbstractExtractor(String tag) {
        this.tag = tag;
    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(tag);
    }
}
