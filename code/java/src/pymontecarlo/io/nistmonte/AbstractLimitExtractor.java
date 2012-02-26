package pymontecarlo.io.nistmonte;

/**
 * Abstract class for the <code>LimitExtractor</code> interface.
 * 
 * @author ppinard
 */
public abstract class AbstractLimitExtractor extends AbstractExtractor
        implements LimitExtractor {

    /**
     * Creates a new <code>AbstractLimitExtractor</code>.
     * 
     * @param tags
     *            required XML tag(s)
     */
    public AbstractLimitExtractor(String... tags) {
        super(tags);
    }

}
