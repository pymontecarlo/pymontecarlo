package pymontecarlo.io.nistmonte;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.jdom.Element;

/**
 * Abstract implementation of the extractor interface.
 * 
 * @author ppinard
 */
public abstract class AbstractExtractor implements Extractor {

    /** XML tag. */
    private final Set<String> tags;



    /**
     * Creates a new <code>AbstractExtractor</code>.
     * 
     * @param tags
     *            required XML tag(s)
     */
    public AbstractExtractor(String... tags) {
        this.tags = new HashSet<String>();
        this.tags.addAll(Arrays.asList(tags));
    }



    @Override
    public boolean canExtract(Element element) {
        return tags.contains(element.getName());
    }
}
